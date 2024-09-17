   @echo off
   C:\Users\bnsoh2\AppData\Roaming\Python\Scripts\poetry.exe run gunicorn --workers 2 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8080 --timeout 300 app:app