# Hackaton Trivia - Минимальная документация

## 🚀 Быстрый старт

```bash
# Установите зависимости
pip install fastapi uvicorn sqlalchemy bcrypt python-dotenv

# Запустите приложение
python main.py

### 2. Настройка окружения

Создайте файл .env:

DB_HOST=localhost
DB_PORT=5432
DB_NAME=hackaton_trivia
DB_USER=postgres
DB_PASSWORD=your_password

SERVER_HOST=0.0.0.0
SERVER_PORT=3425

### 3. База данных
PostgreSQL требуется для работы

Таблицы создаются автоматически при первом запуске

Вопросы загружаются из OpenTriviaDB API

📍### Основные эндпоинты
🔐 Аутентификация
POST /api/v1/trivia/register - Регистрация

POST /api/v1/trivia/login - Вход

🎯 Игра
GET /api/v1/trivia/question - Случайный вопрос

GET /api/v1/room - Список комнат

POST /api/v1/room - Создать комнату

PATCH /api/v1/room/{id}/join - Войти в комнату

POST /api/v1/room/{id}/start - Начать игру

🔌 WebSocket
WS /ws/room/{room_id} - Реальное время в комнате

🏗️ Архитектура

FastAPI приложение
├── Controller (маршруты)
├── Service (бизнес-логика) 
├── Repository (работа с БД)
└── Models (SQLAlchemy модели)

📚 Используемые библиотеки
🎯 Основные
FastAPI - веб-фреймворк

SQLAlchemy - ORM для работы с БД

Uvicorn - ASGI сервер

Pydantic - валидация данных

 🔐 Безопасность
Bcrypt - хеширование паролей

⚙️ Утилиты
python-dotenv - работа с переменными окружения

Requests - HTTP запросы к OpenTriviaDB API

Jinja2 - шаблонизация HTML

🏗️ Основные классы и методы
⚙️ Settings (config/config.py)
class Settings:
    def __init__()  # Загрузка переменных окружения
    def getDatabaseConnectionURL() -> str  # Получить URL подключения к БД

🗄️ Модели (model/Models.py)
class Base(DeclarativeBase)  # Базовый класс SQLAlchemy
class User(Base)  # Пользователь
    to_dict() -> dict  # Сериализация в словарь

class Room(Base)  # Игровая комната  
    to_dict() -> dict  # Сериализация в словарь

class Question(Base)  # Вопрос викторины
    to_dict() -> dict  # Сериализация с вариантами ответов

class RoomParticipant(Base)  # Связь пользователь-комната
class PlayerAnswer(Base)  # Ответы игроков

📊 Репозитории (repository/)
UserRepository
class UserRepository:
    login(user: User) -> User  # Аутентификация пользователя
    register(user: User) -> User  # Регистрация нового пользователя
    getUserById(user_id: int) -> User  # Найти пользователя по ID
    findById(user_id: int) -> User  # Альтернативный поиск по ID
    
 RoomRepository
 class RoomRepository:
    findAll() -> List[Room]  # Все комнаты
    findById(room_id: int) -> Room  # Комната по ID
    createRoom(room: Room) -> Room  # Создать комнату
    addParticipant(room_id, user_id)  # Добавить участника
    removeParticipant(room_id, user_id)  # Удалить участника
    verify_room_password() -> bool  # Проверить пароль комнаты
    changeRunning(room_id)  # Переключить статус игры
    
 QuestionRepository
 class QuestionRepository:
    createQuestion(question: Question) -> Question  # Создать вопрос
    findById(question_id: int) -> Question  # Вопрос по ID  
    findRandom() -> Question  # Случайный вопрос
    addQustionsFromOpenTriviaDB()  # Загрузить вопросы из API
    
 PlayerAnswerRepository
 class PlayerAnswerRepository:
    save(answer: PlayerAnswer)  # Сохранить ответ
    get_by_room_and_question() -> List  # Ответы для комнаты и вопроса
    get_all_for_room() -> List  # Все ответы в комнате
    
🎯 Сервисы (service/)
AuthenticationService
class AuthenticationService:
    register(user: User) -> User  # Зарегистрировать пользователя
    login(user: User) -> User  # Войти в систему
    
RoomService
class RoomService:
    get_all_rooms() -> List[Room]  # Все комнаты
    get_room_by_id(room_id) -> Room  # Комната по ID
    create_room(room: Room) -> Room  # Создать комнату
    add_participant()  # Добавить участника
    remove_participant()  # Удалить участника
    
QuestionService
class QuestionService:
    find_random() -> Question  # Получить случайный вопрос
    
GameService
class GameService:
    start_game(room_id)  # Начать игру в комнате
    submit_answer(room_id, user_id, answer)  # Принять ответ игрока
    get_leaderboard(room_id) -> List  # Таблица лидеров
    
🎮 Контроллеры (controller/)
AuthController
@router.post("/api/v1/trivia/register")  # Регистрация
@router.post("/api/v1/trivia/login")  # Авторизация

RoomController

@router.get("/api/v1/room")  # Список комнат
@router.post("/api/v1/room")  # Создать комнату
@router.patch("/api/v1/room/{id}/join")  # Войти в комнату
@router.websocket("/ws/room/{room_id}")  # WebSocket подключение
@router.post("/api/v1/room/{room_id}/start")  # Начать игру

🎮 Как играть
Зарегистрируйтесь или войдите

Создайте комнату или присоединитесь к существующей

Начните игру когда все готовы

Отвечайте на вопросы через WebSocket

Следите за рейтингом в реальном времени

⚙️ Основные настройки
Порт сервера: 3425

База данных: PostgreSQL

Автогенерация вопросов при запуске

WebSocket для реального времени

Приложение готово к работе после настройки БД и запуска! 🚀