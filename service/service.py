from repository.UserRepository import UserRepository
from model.Models import User
import bcrypt

class AuthenticationService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register(self, user: User):
        try:
            password_bytes = user.password.encode('utf-8')
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password_bytes, salt)
            user.password = hashed_password.decode('utf-8')

            user_from_database = self.user_repository.register(user)
            return user_from_database
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