from typing import List, Optional
from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from model.Models import Question, Base
from config.config import Settings

class QuestionRepository:
    
    settings: Settings
    
    engine: Engine
    
    def __init__(self):
        
        self.settings = Settings()
        
        DATABASE_URL = self.settings.getDatabaseConnectionURL()
        
        self.engine = create_engine(DATABASE_URL)
        
        Base.metadata.create_all(bind=self.engine)
        
    def createQuestion(self, question: Question):
        try:
            with Session(self.engine) as session:
                existing = session.execute(select(Question).where(Question.text == question.text)).scalar_one_or_none()
                if existing:
                    raise ValueError('Question with this text already exist')                
                
                session.add(question)                
                session.commit()
                session.refresh(question)
                return question
        except SQLAlchemyError as e:
            raise RuntimeError(f'Failed to create question: {e}')
        
    def findById(self, question_id: int):
        try:
            with Session(self.engine) as session:
                return session.get(Question, question_id)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Failed to fetch question {question_id}: {e}')
    
    def findRandom(self):
        try:
            with Session(self.engine) as session:
                stmt = select(Question).order_by(func.random()).limit(1)
                return session.scalar(stmt)
        except SQLAlchemyError as e:
            raise RuntimeError(f'Failed to fetch random question: {e}')
        
    