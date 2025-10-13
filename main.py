from controller.controller import app
from config.config import Settings

def main():
    settings = Settings()
    app.run(
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        debug=True,
    )
    
if __name__ == '__main__':
    main()