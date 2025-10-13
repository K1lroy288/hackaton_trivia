from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template
from model.Models import User, Role
from service.service import AuthenticationService

auth_service = AuthenticationService()
app = Flask("Trivia")
""" Парсим json и отправляем структуру на сервис"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/api/v1/trivia/register", methods = ['POST'])
def controller_register():
    try:
        data = request.get_json()

        user = User()
        user.username = data['username']
        user.password = data['password']

        return jsonify(auth_service.register(user).to_dict()), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error", "details": str(e)}), 500

@app.route("/api/v1/trivia/login", methods = ['POST'])
def controller_login():
    try:
        data = request.get_json()
        user = User()
        user.username = data['username']
        user.password = data['password']

        return jsonify(auth_service.login(user).to_dict()), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Error", "details": str(e)}), 500