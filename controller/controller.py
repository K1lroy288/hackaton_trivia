from datetime import datetime, timezone
from flask import Flask, request, jsonify
from model.User import User
from service.service import AuthenticationService

auth_service = AuthenticationService()
app = Flask("Trivia")
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
        user.createdAt = datetime.now(timezone.utc)

        return jsonify(auth_service.register(user)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error", "details": str(e)}), 500

@app.route("/api/v1/trivia/login", methods = ['GET'])
def controller_login():
    try:
        data = request.get_json()
        user.id = data['id']
        user.username = data['username']
        user.password = data['password']
        user.roles = data['roles']

        return jsonify(auth_service.login(user).to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error", "details": str(e)}), 500