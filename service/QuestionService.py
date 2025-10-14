from model.Models import Question
from repository.QuestionRepository import QuestionRepository

class QuestionService:
    quest_repository: QuestionRepository
    def __init__(self):
        self.quest_repository = QuestionRepository()

    def find_random(self):
        quest = self.quest_repository.findRandom()
        return quest