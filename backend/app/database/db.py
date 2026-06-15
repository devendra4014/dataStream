from abc import ABC, abstractmethod

from sqlalchemy import Engine, create_engine, inspect
from sqlalchemy.orm import Session, sessionmaker

from app.middleware.logger_middleware import get_logger
from app.models.user_model import Base, User
from app.schemas.connection_settings import DuckDBSettings

logger = get_logger(__name__)


class Database(ABC):
    @abstractmethod
    def get_engine(self) -> Engine:
        pass

    @abstractmethod
    def get_session(self) -> Session:
        pass


class DuckDBClient(Database):
    def __init__(self, duckdb_settings: DuckDBSettings):

        if isinstance(duckdb_settings, dict):
            self.database_url = duckdb_settings["database_url"]
        else:
            self.database_url = duckdb_settings.database_url

        self.engine = create_engine(self.database_url)
        self.session = sessionmaker(bind=self.engine)

        logger.info("duckdb engine and session parameters are initialised.")

        # create user table if not created.
        Base.metadata.create_all(self.engine)
        self.add_dummy_user()

    # Get database engine details
    def get_engine(self):
        return self.engine

    def get_session(self):
        return self.session()

    def is_connected(self) -> bool:
        try:
            self.engine.connect()
            logger.info("Duckdb Database is connected.")
            return {"status": "success", "message": "Duckdb Database is connected."}
        except Exception as e:
            logger.error(f"error...[{str(e)}]")
            return {"status": "error", "message": "Duckdb Database is not connected."}

    # get all table names
    def get_all_tables(self):
        inspector = inspect(self.engine)
        table_names = inspector.get_table_names()
        return table_names

    def add_dummy_user(self):
        session = self.session()
        try:
            # check if user already exists
            existing = session.query(User).filter(User.username == "admin").first()
            if existing:
                print("User already exists")
                return

            import bcrypt

            # create dummy user
            dummy_user = User(
                username="admin",
                email="admin@test.com",
                hashed_password=bcrypt.hashpw(
                    "admin123".encode("utf-8"), bcrypt.gensalt(rounds=12)
                ),
            )

            session.add(dummy_user)
            session.commit()

            print("Dummy user created successfully")

        except Exception as e:
            session.rollback()
            print(f"Error creating user: {e}")

        finally:
            session.close()

    # def get_db_session(self) -> Generator:
    #     """Get the Database session."""
    #     db_session = self.session()
    #     try:
    #         yield db_session
    #     finally:
    #         db_session.close()  # Ensures every request closes its connection cleanly
