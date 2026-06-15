from sqlalchemy.orm import Session

from app.middleware.logger_middleware import get_logger
from app.models.user_model import User

logger = get_logger(__name__)


class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_by_username(self, username: str):

        try:
            logger.info(f"Fetching user: {username}")

            user = self.session.query(User).filter(User.username == "admin").first()
            logger.info(f"Got User : {user}")
            return user

        except Exception as e:
            logger.exception(f"Error fetching user {username}: {str(e)}")
            raise
