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


''' Citation 2 '''

# route
@server.route("/login",methods=["POST"])
def login():
    auth = request.authorization # auth.username , auth.password
    if not auth:
        return "missing credentials", 401
    
    # check db for username and password
    cursor = mysql.connection.cursor()
    res = cursor.execute(
        "SELECT email, password fro user where email=%s", (auth.username,)
    ) # email is being used as "username" and we will pass it as a tuple.

    if res > 0:
        user_row = cursor.fetchone()
        email = user_row[0]
        password = user_row[1]

        if email != auth.username or auth.password != password:
            return "Invalid Credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
    else:
        return "Invalid Credentials", 401
    

''' Citation 4 '''

@server.route("/validate", methods=["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]

    if not encoded_jwt:
        return "missing credentials", 401

    encoded_jwt = encoded_jwt.split(" ")[1]

    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms=["HS256"]
        )
    except:
        return "not authorized", 403

    return decoded, 200


''' Citation 1 '''

def createJWT(username, secret, authx): # authx is to check for admin priviledges (whether user is administartor or not)
    return jwt.encode(
        payload={
            "username": username,
            "exp": datetime.datetime.now(tz=datetime.timezone.utc) 
            + datetime.timedelta(days=1), # Token will expire after 1 day from issued date
            "iat": datetime.datetime.utcnow(), # Token issued date and time
            "admin": authx # Admin Priviledges (True/False)
        },
        key=secret,
        algorithm="HS256",
    )

if __name__ == "__main__":
    
    ''' Citation 3 '''

    # Start server
    # Our application wil run on port 5000
    # # host is set to 0.0.0.0 to allow our application to listen on any public IP address on our host. Default is localhost which means our API won't be available externally
    server.run(host="0.0.0.0", port=5000)  