# main.py
import os
from user_interface import create_app

app = create_app()

if __name__ == "__main__":
    if os.environ.get("ENV") == "production":
        # In production, we expect gunicorn to serve the app from wsgi.py
        pass
    else:
        # Running locally
        app.launch(share=True)
