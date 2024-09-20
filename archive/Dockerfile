   # Use an official Python runtime as a parent image
   FROM python:3.9-slim

   # Set environment variables
   ENV PYTHONUNBUFFERED=1 \
       PYTHONDONTWRITEBYTECODE=1 \
       PIP_NO_CACHE_DIR=off \
       PIP_DISABLE_PIP_VERSION_CHECK=on \
       PIP_DEFAULT_TIMEOUT=100 \
       POETRY_VERSION=1.8.3 \
       POETRY_HOME="/opt/poetry" \
       POETRY_VIRTUALENVS_IN_PROJECT=true \
       POETRY_NO_INTERACTION=1 \
       PYSETUP_PATH="/opt/pysetup" \
       VENV_PATH="/opt/pysetup/.venv"

   # prepend poetry and venv to path
   ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

   # Install poetry
   RUN pip install "poetry==$POETRY_VERSION"

   # Set the working directory in the container
   WORKDIR $PYSETUP_PATH

   # Copy only requirements to cache them in docker layer
   COPY pyproject.toml poetry.lock* ./

   # Install dependencies
   RUN poetry install --no-root

   # Copy the current directory contents into the container
   COPY . .

   # Make port 8080 available to the world outside this container
   EXPOSE 8080

   # Run app.py when the container launches
   CMD ["poetry", "run", "gunicorn", "--workers", "2", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8080", "--timeout", "300", "app:app"]