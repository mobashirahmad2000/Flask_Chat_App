Chat Application using Flask and Socket.IO
A real-time chat application built with Flask and Socket.IO. Users can register, log in, create chat rooms, and exchange messages within those rooms in real-time.

Features
User registration and login with password hashing.
Creation of unique chat rooms.
Real-time messaging using Socket.IO.
Message history for each chat room.
Joining and leaving chat rooms.
Getting Started
Prerequisites:

Python 3.7+
MongoDB database (configured as per the provided settings)
Flask and Flask extensions (Flask-MongoEngine, Flask-SocketIO)
Installation:

git clone https://github.com/yourusername/chat-app.git
cd chat-app
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
Usage:

To Start the Flask application:
python app.py
Access the application at http://localhost:5000.

Register, log in, and start chatting in real-time!
API Endpoints
/api/register (POST): Register a new user.
/api/login (POST): Log in a user.
/api/logout (POST): Log out a user.
/api/chat/rooms (POST): Create a new chat room.
/api/chat/rooms (GET): Get a list of all chat rooms.
/api/chat/rooms/<room_id> (GET): Get details of a specific chat room.
/api/chat/rooms/<room_id>/messages (POST): Send a message to a chat room.
/api/chat/rooms/<room_id>/join (POST): Join a chat room.
/api/chat/rooms/<room_id>/messages (GET): Get messages for a chat room.
