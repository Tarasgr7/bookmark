from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from src.constans.http_status_code import *
import validators
from src.database import mongo, User
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flasgger import swag_from
from bson.objectid import ObjectId
from datetime import datetime
auth = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth.post('/register')
@swag_from('./docs/auth/register.yaml')
def register():
    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if len(password) <= 6:
        return jsonify({'error': "Password is too short"}), HTTP_400_BAD_REQUEST

    if len(username) < 3:
        return jsonify({'error': "Username is too short"}), HTTP_400_BAD_REQUEST

    if not username.isalnum() or " " in username:
        return jsonify({'error': "Username should be alphanumeric, also no spaces"}), HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'error': "Email is not valid"}), HTTP_400_BAD_REQUEST

    if mongo.db.users.find_one({"email": email}):
        return jsonify({'error': "Email is taken"}), HTTP_409_CONFLICT

    if mongo.db.users.find_one({"username": username}):
        return jsonify({'error': "Username is taken"}), HTTP_409_CONFLICT

    pwd_hash = generate_password_hash(password)

    user = {
        "username": username,
        "email": email,
        "password": pwd_hash,
        "created_at": datetime.utcnow()
    }

    mongo.db.users.insert_one(user)

    return jsonify({
        'message': "User created",
        'user': {
            'username': username, "email": email
        }

    }), HTTP_201_CREATED


@auth.post('/login')
@swag_from('./docs/auth/login.yaml')
def login():
    email = request.json.get('email', '')
    password = request.json.get('password', '')

    user = mongo.db.users.find_one({"email": email})

    if user:
        is_pass_correct = check_password_hash(user['password'], password)

        if is_pass_correct:
            refresh = create_refresh_token(identity=str(user['_id']))
            access = create_access_token(identity=str(user['_id']))

            return jsonify({
                'user': {
                    'refresh': refresh,
                    'access': access,
                    'username': user['username'],
                    'email': user['email']
                }

            }), HTTP_200_OK

    return jsonify({'error': 'Wrong credentials'}), HTTP_401_UNAUTHORIZED


@auth.get("/me")
@jwt_required()
def me():
    user_id = get_jwt_identity()

    user = mongo.db.users.find_one({"_id": ObjectId(user_id)})

    if not user:
        return jsonify({'error': 'User not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'username': user['username'],
        'email': user['email']
    }), HTTP_200_OK


@auth.get('/token/refresh')
@jwt_required(refresh=True)
def refresh_users_token():
    identity = get_jwt_identity()
    access = create_access_token(identity=identity)
    return jsonify({
        'access': access
    }), HTTP_200_OK
