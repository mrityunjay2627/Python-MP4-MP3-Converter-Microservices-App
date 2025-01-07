import os, json, pika, gridfs
from flask import Flask, request
from flask_pymongo import PyMongo
from gateway import access

server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)    

fs = gridfs.GridFS(mongo.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

@server.route('/login',methods=["POST"])

# It will communicate with our auth service to log the user in and assign a token to that user 
def login():
    token,err = access.login(request)
