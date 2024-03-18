from dotenv import load_dotenv

import app
from app import factory
from app.factory import sql_db
from app.models import VideoData

load_dotenv()
app = factory.create_app(celery=app.celery)


@app.shell_context_processor
def make_shell_context():
    return {
        "db": sql_db,
        "vd": VideoData
    }


if __name__ == "__main__":
    app.run(port=8000, debug=True, use_reloader=True)
