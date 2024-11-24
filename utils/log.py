import asyncio
import logging
import time
from contextvars import ContextVar
from typing import Optional

import httpx

from utils.variables import ENV, LOKI_URL

# ContextVar to store the trace ID for the current context
trace_id_var = ContextVar("trace_id", default="")


class CustomFormatter(logging.Formatter):
    def format(self, record):
        record.trace_id = trace_id_var.get()
        return super().format(record)


class AsyncLokiHandler(logging.Handler):
    def __init__(self, url: str, labels: Optional[dict] = None):
        super().__init__()
        self.url = url
        self.labels = labels or {}
        self.queue = asyncio.Queue()
        self.client: Optional[httpx.AsyncClient] = None
        self.task: Optional[asyncio.Task] = None
        self.last_error_time = 0
        self.error_count = 0
        self.max_backoff = 60  # Maximum backoff time in seconds

    async def initialize(self):
        if not self.client:
            self.client = httpx.AsyncClient()
        if not self.task:
            self.task = asyncio.create_task(self.sender())

    async def sender(self):
        while True:
            record = await self.queue.get()
            try:
                await self.send_log(record)
                self.error_count = 0  # Reset error count on successful send
            except Exception as e:
                self.handle_error(e)
            finally:
                self.queue.task_done()

    async def send_log(self, record):
        if not self.client:
            await self.initialize()
        log_entry = self.format(record)
        payload = {
            "streams": [
                {
                    "stream": self.labels,
                    "values": [[str(int(record.created * 1e9)), log_entry]]
                }
            ]
        }
        headers = {'Content-type': 'application/json'}
        response = await self.client.post(self.url, json=payload, headers=headers)
        response.raise_for_status()

    def handle_error(self, error):
        current_time = time.time()
        if current_time - self.last_error_time > self.max_backoff:
            self.error_count = 0

        self.error_count += 1
        backoff_time = min(2 ** self.error_count, self.max_backoff)
        self.last_error_time = current_time

        # Log the error to console, but don't try to send it to Loki
        print(f"Failed to send log to Loki: {error}. Backing off for {backoff_time} seconds.")
        asyncio.create_task(self.backoff(backoff_time))

    async def backoff(self, seconds):
        await asyncio.sleep(seconds)

    def emit(self, record):
        asyncio.create_task(self.async_emit(record))

    async def async_emit(self, record):
        if not self.client:
            await self.initialize()
        await self.queue.put(record)

    async def close(self):
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        await self.queue.join()
        if self.client:
            await self.client.aclose()
            self.client = None


class AsyncLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET):
        super().__init__(name, level)
        self._async_handlers = []

    def addHandler(self, hdlr):
        if isinstance(hdlr, AsyncLokiHandler):
            self._async_handlers.append(hdlr)
        super().addHandler(hdlr)

    def handle(self, record):
        # Only use non-async handlers for immediate logging
        for handler in self.handlers:
            if not isinstance(handler, AsyncLokiHandler):
                handler.handle(record)

        # Use async handlers separately
        for handler in self._async_handlers:
            handler.emit(record)


logging.setLoggerClass(AsyncLogger)


def get_logger(name: str) -> AsyncLogger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s')
        console_handler.setFormatter(console_formatter)

        # Loki handler
        loki_handler = AsyncLokiHandler(
            url=LOKI_URL,
            labels={"service": "login-auth", "env": ENV}
        )
        loki_handler.setLevel(logging.DEBUG)
        loki_formatter = CustomFormatter('%(asctime)s - %(name)s - %(levelname)s - [%(trace_id)s] - %(message)s')
        loki_handler.setFormatter(loki_formatter)

        # Add handlers to logger
        logger.addHandler(console_handler)
        logger.addHandler(loki_handler)

    return logger


# Create a global logger instance
logger = get_logger("auth_and_order_service")
