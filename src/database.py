from flask_pymongo import PyMongo
from datetime import datetime
import string
import random

mongo = PyMongo()

class User:
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password
        self.created_at = datetime.utcnow()
        self.updated_at = None

    def save(self):
        user_data = {
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        return mongo.db.users.insert_one(user_data)

    @staticmethod
    def find_by_username(username):
        return mongo.db.users.find_one({"username": username})

    @staticmethod
    def find_by_email(email):
        return mongo.db.users.find_one({"email": email})

    def __repr__(self):
        return f"<User('{self.username}', '{self.email}')>"

class Bookmark:
    def __init__(self, body, url, user_id):
        self.body = body
        self.url = url
        self.short_url = self.generate_short_characters()
        self.visits = 0
        self.user_id = user_id
        self.created_at = datetime.utcnow()
        self.updated_at = None

    def generate_short_characters(self):
        characters = string.digits + string.ascii_lowercase
        picked_chars = ''.join(random.choices(characters, k=3))


        existing_link = mongo.db.bookmarks.find_one({"short_url": picked_chars})
        if existing_link:
            return self.generate_short_characters()
        return picked_chars

    def save(self):
        bookmark_data = {
            "body": self.body,
            "url": self.url,
            "short_url": self.short_url,
            "visits": self.visits,
            "user_id": self.user_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
        return mongo.db.bookmarks.insert_one(bookmark_data)

    @staticmethod
    def find_by_short_url(short_url):
        return mongo.db.bookmarks.find_one({"short_url": short_url})

    @staticmethod
    def update_visits(short_url):
        return mongo.db.bookmarks.update_one(
            {"short_url": short_url},
            {"$inc": {"visits": 1}}
        )

    def __repr__(self):
        return f"<Bookmark('{self.body}', '{self.url}')>"
