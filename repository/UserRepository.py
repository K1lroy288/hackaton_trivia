from sqlalchemy import create_engine
from sqlalchemy import Engine, select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.Models import User, Base,user_role_table
from config.config import Settings

class UserRepository:
    
    settings: Settings
    engine: Engine
    
    def __init__(self):
        self.settings = Settings()

        DATABASE_URL = self.settings.getDatabaseConnectionURL()

        self.engine = create_engine(DATABASE_URL)
        
        Base.metadata.create_all(bind=self.engine)
        
    def login(self, user: User):
        try:
            with Session(self.engine) as session:
                result = session.execute(select(User).where(User.username == user.username))
                db_user = result.scalar_one_or_none()
                if not db_user:
                    raise Exception('User with such username is already exist')
                return db_user
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of repository login of user {user.id}: {e}')
    
    def register(self, user: User):
        try:
            with Session(self.engine) as session:
                result = session.execute(select(User).where(User.username == user.username))
                db_user = result.scalar_one_or_none()
                if db_user:
                    raise ValueError('User with such username is already exist')
                session.add(user)
                session.commit()
                session.refresh(user)
                session.execute(
                    user_role_table.insert().values(user_id=user.id, role="USER")
                )
                return user
        except SQLAlchemyError as e:
            raise RuntimeError(f"DB error: {e}")
            
                    
