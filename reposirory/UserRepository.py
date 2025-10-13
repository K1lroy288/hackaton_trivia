from sqlalchemy import create_engine
from sqlalchemy import create_engine
from sqlalchemy import Engine
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from model.User import User
from config.config import Settings
from datetime import datetime

class UserRepository:
    
    settings: Settings
    engine: Engine
    
    def __init__(self):
        self.settings = Settings()

        DATABASE_URL = self.settings.getDatabaseConnectionURL()

        self.engine = create_engine(DATABASE_URL)
        
    def login(self, user: User):
        try:
            with Session(self.engine) as session:
                db_user = session.get(User, user.id)
                return db_user
        except SQLAlchemyError as e:
            raise RuntimeError(f'Error of repository login of user {user.id}: {e}')
    
    def register(self, user: User):
        try:
            with Session(self.engine) as session:
                db_user = session.get(user.username)
                if db_user:
                    raise Exception('User with such username is already exist')
                session.add(user)
                session.commit()
                session.refresh(user)
                return user
        except Exception as e:
            print(e)
                    
