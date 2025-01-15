from flask import Blueprint, request, jsonify
from src.database import mongo
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.constans.http_status_code import *
import validators
from flasgger import swag_from
from bson.objectid import ObjectId, InvalidId
from datetime import datetime

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks/")


def validate_object_id(id):
    if not ObjectId.is_valid(id):
        return False
    return True


@bookmarks.route('/', methods=['GET', 'POST'])
@jwt_required()
def handle_bookmarks():
    current_user = get_jwt_identity()
    if request.method == 'POST':
        data = request.get_json()
        body = data.get('body', '')
        url = data.get('url', '')

        if not validators.url(url):
            return jsonify({'error': 'Invalid URL'}), HTTP_400_BAD_REQUEST

        if mongo.db.bookmarks.find_one({"url": url, "user_id": ObjectId(current_user)}):
            return jsonify({'error': 'URL already exists'}), HTTP_409_CONFLICT

        bookmark = {
            "url": url,
            "body": body,
            "user_id": ObjectId(current_user),
            "short_url": "",
            "visits": 0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        result = mongo.db.bookmarks.insert_one(bookmark)

        return jsonify({
            'id': str(result.inserted_id),
            'url': bookmark['url'],
            'short_url': bookmark['short_url'],
            'visit': bookmark['visits'],
            'body': bookmark['body'],
            'created_at': bookmark['created_at'],
            'updated_at': bookmark['updated_at'],
        }), HTTP_201_CREATED

    else:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)
        skips = (page - 1) * per_page

        bookmarks_list = list(mongo.db.bookmarks.find({"user_id": ObjectId(current_user)}).skip(skips).limit(per_page))

        data = []
        for bookmark in bookmarks_list:
            data.append({
                'id': str(bookmark['_id']),
                'url': bookmark['url'],
                'short_url': bookmark['short_url'],
                'visit': bookmark['visits'],
                'body': bookmark['body'],
                'created_at': bookmark['created_at'],
                'updated_at': bookmark['updated_at'],
            })

        total_count = mongo.db.bookmarks.count_documents({"user_id": ObjectId(current_user)})
        meta = {
            "page": page,
            'pages': (total_count + per_page - 1) // per_page,
            'total_count': total_count,
            'has_next': skips + per_page < total_count,
            'has_prev': page > 1
        }

        return jsonify({'data': data, 'meta': meta}), HTTP_200_OK


@bookmarks.route('/<string:id>', methods=['GET'])
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    if not validate_object_id(id):
        return jsonify({'error': 'Invalid ID format'}), HTTP_400_BAD_REQUEST

    bookmark = mongo.db.bookmarks.find_one({"_id": ObjectId(id), "user_id": ObjectId(current_user)})
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), HTTP_404_NOT_FOUND

    return jsonify({
        'id': str(bookmark['_id']),
        'url': bookmark['url'],
        'visit': bookmark['visits'],
        'body': bookmark['body'],
        'created_at': bookmark['created_at'],
        'updated_at': bookmark['updated_at'],
    }), HTTP_200_OK


@bookmarks.route('/<string:id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_bookmark(id):
    current_user = get_jwt_identity()
    if not validate_object_id(id):
        return jsonify({'error': 'Invalid ID format'}), HTTP_400_BAD_REQUEST

    bookmark = mongo.db.bookmarks.find_one({"_id": ObjectId(id), "user_id": ObjectId(current_user)})
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), HTTP_404_NOT_FOUND

    data = request.get_json()
    body = data.get('body', bookmark['body'])
    url = data.get('url', bookmark['url'])

    if not validators.url(url):
        return jsonify({'error': 'Invalid URL'}), HTTP_400_BAD_REQUEST

    mongo.db.bookmarks.update_one(
        {"_id": ObjectId(id)},
        {"$set": {
            "body": body,
            "url": url,
            "updated_at": datetime.utcnow()
        }}
    )

    updated_bookmark = mongo.db.bookmarks.find_one({"_id": ObjectId(id)})

    return jsonify({
        'id': str(updated_bookmark['_id']),
        'url': updated_bookmark['url'],
        'visit': updated_bookmark['visits'],
        'body': updated_bookmark['body'],
        'created_at': updated_bookmark['created_at'],
        'updated_at': updated_bookmark['updated_at'],
    }), HTTP_200_OK


@bookmarks.route('/<string:id>', methods=['DELETE'])
@jwt_required()
def delete_bookmark(id):
    current_user = get_jwt_identity()
    if not validate_object_id(id):
        return jsonify({'error': 'Invalid ID format'}), HTTP_400_BAD_REQUEST

    bookmark = mongo.db.bookmarks.find_one({"_id": ObjectId(id), "user_id": ObjectId(current_user)})
    if not bookmark:
        return jsonify({'error': 'Bookmark not found'}), HTTP_404_NOT_FOUND

    mongo.db.bookmarks.delete_one({"_id": ObjectId(id)})
    return jsonify({'message': 'Bookmark deleted'}), HTTP_200_OK


@bookmarks.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()

    bookmarks = mongo.db.bookmarks.find({"user_id": ObjectId(current_user)})

    data = []
    for bookmark in bookmarks:
        data.append({
            'visits': bookmark['visits'],
            'url': bookmark['url'],
            'id': str(bookmark['_id']),
            'short_url': bookmark['short_url'],
        })

    return jsonify({'data': data}), HTTP_200_OK
