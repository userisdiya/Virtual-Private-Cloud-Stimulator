from flask import Flask, session, redirect, url_for
from routes import main_routes  # Import the main_routes blueprint

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Secret key for session management

app.register_blueprint(main_routes)  # Register the blueprint for the routes

if __name__ == '__main__':
    app.run(debug=True)
