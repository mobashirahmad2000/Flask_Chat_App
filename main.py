import datetime
import os
import re

from flask import Flask, request, jsonify, session
from flask_socketio import SocketIO, emit, join_room
from flask_mongoengine import MongoEngine
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.json_encoder = Flask.json_encoder
app.config['SECRET_KEY'] = os.urandom(24)

# Mongodb Connection
app.config['MONGODB_SETTINGS'] = {
    'db': 'chat_app_db',
    'host': 'mongodb-container',
    'port': 27017,
    'username': 'admin',
    'password': 'admin_password'
}

db = MongoEngine(app)
socketio = SocketIO(app)

# Define Models and Schemas
class User(db.Document):
    username = db.StringField(required=True, unique=True)
    email = db.EmailField(required=True, unique=True)
    password_hash = db.StringField(required=True)

    def set_password(self, password):
        # Hash the password and store it in the password_hash field
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        # Check if the provided password matches the stored hashed password
        return check_password_hash(self.password_hash, password)

    def to_json(self):
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
        }

class ChatRoom(db.Document):
    name = db.StringField(required=True, unique=True)
    users = db.ListField(db.ReferenceField(User))

    def to_json(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "users": [str(user.id) for user in self.users],
        }

class Message(db.Document):
    text = db.StringField(required=True)
    sender = db.ReferenceField(User, required=True)
    room = db.ReferenceField(ChatRoom, required=True)
    created_at = db.DateTimeField()

    def to_json(self):
        return {
            "id": str(self.id),
            "text": self.text,
            "sender_id": str(self.sender.id),
            "room_id": str(self.room.id),
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
        }
# Routes
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json

    existing_user = User.objects(username=data['username']).first()
    existing_email = User.objects(email=data['email']).first()

    if existing_user or existing_email:
        return jsonify({"message": "Username or email already exists"}), 400

    if not re.match(r'^(?=.*\d)(?=.*[A-Z])(?=.*[@#$%^&+=]).+$', data['password']):
        return jsonify({"message": "Invalid password format"}), 400

    if not re.match(r'^\S+@\S+\.\S+$', data['email']):
        return jsonify({"message": "Invalid email format"}), 400

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])  # Use the set_password method to hash the password
    user.save()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json

    user = User.objects(username=data['username']).first()

    if user and user.check_password(data['password']):

        session['user_id'] = str(user.id)
        return jsonify({"message": "Login successful"}), 200
    else:
        return jsonify({"message": "Invalid username or password"}), 401


@app.route('/api/logout', methods=['POST'])
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        return jsonify({"message": "Logout successful"}), 200
    else:
        return jsonify({"message": "No user logged in"}), 401


@app.route('/api/chat/rooms', methods=['POST'])
def create_chat_room():
    data = request.json

    existing_room = ChatRoom.objects(name=data['name']).first()
    if existing_room:
        return jsonify({"message": "Chat room with this name already exists"}), 400

    chat_room = ChatRoom(name=data['name'])
    chat_room.save()

    return jsonify({"message": "Chat room created successfully"}), 201

@app.route('/api/chat/rooms', methods=['GET'])
def get_chat_rooms():
    chat_rooms = ChatRoom.objects.all()
    chat_room_list = [room.to_json() for room in chat_rooms]
    return jsonify(chat_room_list)

@app.route('/api/chat/rooms/<string:room_id>', methods=['GET'])
def get_chat_room_details(room_id):
    chat_room = ChatRoom.objects(id=room_id).first()
    if not chat_room:
        return jsonify({"message": "Chat room not found"}), 404

    return jsonify(chat_room.to_json()), 200

@app.route('/api/chat/rooms/<string:room_id>/messages', methods=['POST'])
def send_message(room_id):
    data = request.json
    message_text = data.get('message')

    if not message_text:
        return jsonify({"message": "Message text is required"}), 400

    sender_id = session.get('user_id')

    if not sender_id:
        return jsonify({"message": "User not authenticated"}), 401

    chat_room = ChatRoom.objects(id=room_id).first()
    if not chat_room:
        return jsonify({"message": "Chat room not found"}), 404

    sender = User.objects(id=sender_id).first()
    message = Message(
        text=message_text,
        sender=sender,
        room=chat_room,
        created_at=datetime.datetime.utcnow()
    )
    message.save()

    if sender not in chat_room.users:
        chat_room.users.append(sender)
        chat_room.save()

    socketio.emit('new_message', {
        'message_id': str(message.id),
        'text': message_text,
        'sender_id': sender_id,
        'room_id': room_id,
        'created_at': message.created_at.strftime('%Y-%m-%d %H:%M:%S')
    }, room=room_id)

    return jsonify({"message": "Message sent successfully"}), 201
@app.route('/api/chat/rooms/<string:room_id>/join', methods=['POST'])
def join_chat_room(room_id):
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"message": "User is not logged in or invalid user ID"}), 401

    chat_room = ChatRoom.objects(id=room_id).first()
    if not chat_room:
        return jsonify({"message": "Chat room not found"}), 404

    user = User.objects(id=user_id).first()
    if user in chat_room.users:
        return jsonify({"message": "User is already a member of this chat room"}), 200

    chat_room.users.append(user)
    chat_room.save()

    join_room(room_id)

    return jsonify({"message": "User joined the chat room successfully"}), 200

@socketio.on('send_message')
def handle_message(data):
    room_id = data['room_id']
    user_id = session.get('user_id')
    if not user_id:
        return

    socketio.emit('new_message', {
        'message_id': str(data.get('message_id')),
        'text': data.get('text'),
        'sender_id': user_id,
        'room_id': room_id,
        'created_at': data.get('created_at')
    }, room=room_id)


@app.route('/api/chat/rooms/<string:room_id>/messages', methods=['GET'])
def get_room_messages(room_id):
    chat_room = ChatRoom.objects(id=room_id).first()
    if not chat_room:
        return jsonify({"message": "Chat room not found"}), 404

    messages = Message.objects(room=chat_room).order_by('-created_at').limit(50)  # Example: Get the last 50 messages
    message_list = [message.to_json() for message in messages]

    return jsonify(message_list), 200


if __name__ == '__main__':
    socketio.run(app, debug=True)


