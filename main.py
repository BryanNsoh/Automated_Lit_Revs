# main.py
import os
from user_interface import create_app

if os.environ.get("ENV") == "production":
    # Running in production (e.g., Cloud Run)
    import logging
    from wsgi import app as application

    # Configure logging
    logging.basicConfig(level=logging.INFO)
else:
    # Running locally
    app = create_app()
    app.launch(share=True)
