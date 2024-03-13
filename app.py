from app import factory
import app

from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    app = factory.create_app(celery=app.celery)
    app.run(port=8000, debug=True, use_reloader=True)
