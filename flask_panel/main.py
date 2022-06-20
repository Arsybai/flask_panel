from app import app
from waitress import serve

print("App running...")

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=8000)