from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool

from utils import store
from utils.constant import *
from utils.variables import DATABASE_URL

# Create the base class for declarative models
Base = declarative_base()


def attach_query_property():
    """Attach a `query` property to the Base class for easy queries."""
    Base.query = store.session.query_property()


def register_models():
    """Register all models to be used with SQLAlchemy."""
    from app.user.models import Users  # noqa: F401
    from app.payments.models import UserPayment  # noqa: F401
    from app.orders.models import Orders  # noqa: F401


def connect_to_database() -> bool:
    """Connect to the database using the provided URI."""
    try:
        connection_uri = DATABASE_URL
        engine = create_engine(
            connection_uri,
            poolclass=StaticPool,  # Use StaticPool for in-memory databases or testing
            echo=False  # Set echo=True for SQL logging during development
        )
    except OperationalError as oe:
        if str(oe.orig).lower() in DATABASE_CONNECTION_ERRORS:
            store.has_connection_established = False
        return store.has_connection_established

    _session = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False
    )
    session = scoped_session(_session)

    store.engine = engine
    store.session = session
    store.has_connection_established = True

    register_models()
    attach_query_property()

    return store.has_connection_established


def disconnect_from_database():
    """Disconnect from the database and clean up resources."""
    if store.session:
        store.session.remove()
    if store.engine:
        store.engine.dispose()
    store.has_connection_established = False


def rollback_session():
    """Rollback the session in case of an error."""
    if store.session:
        store.session.rollback()


def get_db():
    return store.session()
