from flask import Flask
from config import Config
from db import mongo
from routes import auth_bp, main_bp

app = Flask(__name__)
app.config.from_object(Config)

mongo.init_app(app)

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True)
