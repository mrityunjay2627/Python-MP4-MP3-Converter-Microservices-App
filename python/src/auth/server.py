import jwt, datetime, os # auth services
from flask import Flask, request # server
from flask_mysqldb import MySQL # sql database connection

from dotenv import load_dotenv

load_dotenv() # Load environment variables from .env file

server = Flask(__name__)
mysql = MySQL(server)

# config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")
server.config["MYSQL_PORT"] = os.environ.get("MYSQL_PORT")


# route
@server.route("/login",methods=["POST"])
def login():
    auth = request.authorization # auth.username , auth.password
    if not auth:
        return "missing credentials", 401
    
    # check db for username and password
    