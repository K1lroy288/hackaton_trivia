from repository.UserRepository import UserRepository
from model.User import User
import bcrypt

class AuthenticationService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register(self, user: User):
        try:
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(user.password, salt)
            user.password = hashed_password.decode('utf-8')

            self.user_repository.register(user)
        except Exception as e:
            raise RuntimeError(f"Error registration: {e}")

    def login(self, user: User):
        user_from_db = self.user_repository.login(user)
        if not user_from_db:
            raise ValueError("User not found")

        stored_hash = user_from_db.password

        if not bcrypt.checkpw(user.password.encode('utf-8'), stored_hash.encode('utf-8')):
            raise ValueError("Wrong password")

        return  user_from_db