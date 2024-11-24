import json
from fastapi import FastAPI
from fastapi.exceptions import (HTTPException, RequestValidationError)
from fastapi.middleware.cors import CORSMiddleware
from jose.exceptions import JWTError
from sqlalchemy.exc import OperationalError, PendingRollbackError
from starlette.middleware.base import BaseHTTPMiddleware

from app.user.routers import router as user_router
from utils import response, constant, exceptions, middleware, helpers
from utils.database import connect_to_database, disconnect_from_database, rollback_session


def register_routes(server):
    server.include_router(user_router)
    server.include_router(payment_router)
    server.include_router(order_router)
    server.include_router(search_router)


def register_middlewares(server):
    # Initialize CORS
    server.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True
    )


server = FastAPI(
    title="Expense tracker backend.",
    description="This is a service which is responsible for authenticating users",
    docs_url="/api/docs/",
)


# Startup Events
@server.on_event("startup")
async def startup_event():
    connect_to_database()


# Shutdown Events
@server.on_event("shutdown")
async def shutdown_event():
    disconnect_from_database()


# Register Routes
register_routes(server)

# Register Middlewares
register_middlewares(server)

# add logging middleware
server.add_middleware(BaseHTTPMiddleware, dispatch=middleware.optimized_logging_middleware)


# add custom exception handler.
# exception_handlers(server)


@server.exception_handler(RequestValidationError)
async def validation_exception_handler(_, exception):
    errors = helpers.pydantic_error(exception.errors())['body']
    msg = "Invalid data."
    return response.error(constant.UNPROCESSABLE_ENTITY, msg, errors)


@server.exception_handler(OperationalError)
async def database_operational_exception_handler(_, exception):
    conn = exceptions.DatabaseConnectionProblem()
    return response.error(conn.status_code, conn.message)


@server.exception_handler(PendingRollbackError)
async def database_rollback_exception_handler(_, exception):
    rollback_session()


@server.exception_handler(exceptions.DatabaseConnectionProblem)
async def database_connection_exception_handler(_, exception):
    return response.error(exception.status_code, exception.message)


@server.exception_handler(exceptions.GenericError)
async def generic_exception_handler(_, exception):
    return response.error(message=exception.message, status_code=exception.status_code)


@server.exception_handler(exceptions.InternalError)
async def internal_exception_handler(_, exception):
    rollback_session()
    return response.error(exception.status_code, exception.message)


@server.exception_handler(HTTPException)
async def http_exception_handler(_, exception):
    rollback_session()
    return response.error(exception.status_code, exception.detail)


@server.exception_handler(Exception)
async def exception_handler(_, exception):
    rollback_session()
    return response.error(constant.ERROR_INTERNAL_SERVER_ERROR, str(exception))


@server.exception_handler(JWTError)
async def jwt_exception_handler(_, exception):
    rollback_session()
    return response.error(constant.UNPROCESSABLE_ENTITY, str(exception))


@server.exception_handler(exceptions.ValidationError)
async def validation_exception_handler(_, exception):
    rollback_session()
    return response.error(constant.ERROR_BAD_REQUEST, str(exception.message))


@server.exception_handler(json.JSONDecodeError)
async def json_exception_handler(_, exception):
    rollback_session()
    return response.error(constant.UNPROCESSABLE_ENTITY, str(exception))
