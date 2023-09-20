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
MongoDB database 
start from pulling the docker image
docker pull mongo:4.4
up the container by following command
docker run -d --network=my_network --name mongodb-container -e MONGO_INITDB_ROOT_USERNAME=admin -e MONGO_INITDB_ROOT_PASSWORD=admin_password -e MONGO_INITDB_DATABASE=chat_app_db -p 27017:27017 mongo:4.4


You need to create docker network to make the link between the flask app and mongodb 
docker network create chatapp_network

Flask and Flask extensions (Flask-MongoEngine, Flask-SocketIO)
there is a docker file you can build the image by this command 
docker build -t my-flask-app .
To build the container
docker run -d --network=my_network --name flask-app-container -p 5000:5000 my-flask-app

also if it gives error try pulling the base image define in your DockerFile


Installation:
git clone https://github.com/mobashirahmad2000/Flask_Chat_App.git
cd chat-app
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
pip install -r requirements.txt
Usage:

To Start the Flask application:
python main.py
or up the docker container

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
