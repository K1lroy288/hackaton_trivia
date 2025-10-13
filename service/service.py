"""@app.post(/api/v1/trivia/register)
controller_register()
jsonify
user = service_register()
response = user
return response, httpcode

@app.get(/api/v1/trivia/login)
controller_login
jsonify
user = service_login()
response = user
return response, httpcode

service_register()
bcrypt()
repository_register()
rerturn user, err

service_login()
bcrypt()
login_register()
rerturn user, err"""
from model.User import User

class AuthenticationService:
    userRepository: UserRepository
    def register(self, user: User):
        try:
            user.password = bcrypt(user.password)
            UserRepository.register(user)
            return user
        execpt Exception as e:
            print(e)