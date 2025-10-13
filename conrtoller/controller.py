
from datetime import datetime
from flask import Flask, request, jsonify
from model.User import User
from service.service import AuthenticationService
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

app = Flask(__name__)
""" Парсим json и отправляем структуру на сервис"""
@app.route("/api/v1/trivia/register", methods = ['POST'])
def controller_register():
    try:
        data = request.get_json()

        user = User()
        user.id = data['id']
        user.username = data['username']
        user.password = data['password']
        user.roles = data['roles']
        user.createdAt = datetime.utcnow()

        return jsonify(AuthenticationService.register(user).to_dict(), 201)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Ошибка при создании задачи", "details": str(e)}), 500


app.run(debug = True)