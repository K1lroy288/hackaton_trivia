from dotenv import load_dotenv
import os

load_dotenv()

class Settings:
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    
    SERVER_HOST: str
    SERVER_PORT: int
    
    
    def __init__(self):
        self.DB_HOST = os.getenv('DB_HOST')
        self.DB_PASSWORD = os.getenv('DB_PASSWORD')
        self.DB_NAME = os.getenv('DB_NAME')
        self.DB_PORT = os.getenv('DB_PORT')
        self.DB_USER = os.getenv('DB_USER')
        
        self.SERVER_HOST = os.getenv('SERVER_HOST')
        self.SERVER_PORT = os.getenv('SERVER_PORT')
    
    def getDatabaseConnectionURL(self):
        return f'postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'