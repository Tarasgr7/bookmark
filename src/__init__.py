from flask import Flask, redirect, jsonify
import os
from src.auth import auth
from src.bookmarks import bookmarks
from flask_jwt_extended import JWTManager
from src.constans.http_status_code import *
from flasgger import Swagger, swag_from
from src.config.swagger import swagger_config, template
from dotenv import load_dotenv
from src.database import mongo

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv()
    
    if test_config is None:
        app.config.from_mapping(
            SECRET_KEY=os.environ.get("SECRET_KEY"),
            MONGO_URI=os.environ.get("MONGO_URI"),  # Замініть URI MongoDB
            JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),

            SWAGGER={
                'title': "Bookmarks API",
                'uiversion': 3
            }
        )
    else:
        app.config.from_mapping(test_config)

    # Ініціалізація MongoDB
    mongo.init_app(app)
    try:
      mongo.cx.server_info()  # Перевірка підключення
    except Exception as e:
      print(f"Помилка підключення до MongoDB: {e}")
    
    # Реєстрація blueprints
    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)
    
    # JWT менеджер
    JWTManager(app)

    # Swagger документація
    Swagger(app, config=swagger_config, template=template)

    @app.get("/<short_url>")
    @swag_from('./docs/short_url.yaml')
    def redirect_to_url(short_url):
        bookmark = mongo.db.bookmarks.find_one({"short_url": short_url})
        
        if not bookmark:
            return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

        # Збільшуємо лічильник відвідувань
        mongo.db.bookmarks.update_one(
            {"short_url": short_url},
            {"$inc": {"visits": 1}}
        )
        return redirect(bookmark['url'])

    @app.errorhandler(HTTP_404_NOT_FOUND)
    def handle_404(e):
        return jsonify({'error': 'Not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(HTTP_500_INTERNAL_SERVER_ERROR)
    def handle_500(e):
        return jsonify({'error': 'Something went wrong, we are working on it'}), HTTP_500_INTERNAL_SERVER_ERROR
    print("MongoDB client:", mongo)
    

    return app
