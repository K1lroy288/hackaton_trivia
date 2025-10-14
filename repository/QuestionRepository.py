from typing import List, Optional
from sqlalchemy import create_engine, select, Engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func
from model.Models import Question, Base
from config.config import Settings
import requests

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
                existing = session.execute(select(Question).where(Question.question == question.question)).scalar_one_or_none()
                if existing:
                    return
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
    
    def questionCountInDB(self):
        try:
            with Session(self.engine) as session:
               return session.query(func.count(Question.id)).scalar()
        except SQLAlchemyError as e:
            raise RuntimeError(f'Failed to fetch count questions: {e}')
    
    def addQustionsFromOpenTriviaDB(self):
        openTriviaDBURL = "https://opentdb.com/api.php?amount=50&type=multiple"
        response = requests.get(openTriviaDBURL).json()
        questions = response.get('results', [])
        for q in questions:
            questionJSON = Question(
                difficulty=q['difficulty'],
                category=q['category'],
                question=q['question'],
                correct_answer=q['correct_answer'],
                incorrect_answers=q['incorrect_answers'],
            )
            self.createQuestion(questionJSON)
        
        if self.questionCountInDB() < 300:
            self.addQustionsFromOpenTriviaDB()
        
        return False
    