import os, json, pika, gridfs
from flask import Flask, request, send_file # send_file sends the file to the user
from flask_pymongo import PyMongo
from auth_svc import access
from auth import validate
from storage import util
from bson.objectid import ObjectId

server = Flask(__name__)
# server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo_video = PyMongo(
    server,
    uri="mongodb://host.minikube.internal:27017/videos"
)    

mongo_mp3 = PyMongo(
    server,
    uri="mongodb://host.minikube.internal:27017/mp3s"
) 

fs_videos = gridfs.GridFS(mongo_video.db)
fs_mp3s = gridfs.GridFS(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel()

# It will communicate with our auth service to log the user in and assign a token to that user 
@server.route('/login',methods=["POST"])
def login():
    token,err = access.login(request)

    if not err:
        return token
    
    else:
        return err
    

@server.route('/upload', methods=["POST"])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access) # JSoN to Dictionary

    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "Exactly one file is required", 400
        
        for _, f in request.files.items():
            # _ represnts a key for the file
            # f represents the actual file as a value
            err = util.upload(f, fs_videos, channel, access)

            if err:
                return err
            
        return "success!", 200
    else:
        return "not authorized", 401


@server.route('/download', methods=["GET"])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access) # JSoN to Dictionary

    if access["admin"]:
        fid_string = request.args.get("fid")

        if not fid_string:
            return "fid is required",400

        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.mp3')
        except Exception as err:
            print(err)
            return "internal server error", 500

    
    return "not authorized", 401



if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)