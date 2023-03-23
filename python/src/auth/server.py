import jwt, datetime, os
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

config_list = [
    "MYSQL_HOST",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DB",
    "MYSQL_PORT"
]

for config_name in config_list:
    server.config[config_name] = os.environ.get(config_name)

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return missing_credentials_error()

    cur = mysql.connection.cursor()
    res = cur.execute("SELECT email, password FROM user WHERE email=%s", (auth.username,))
    return_value = invalid_credentials_error()
    if res == 0:
        return return_value
    email, password = cur.fetchone()
    if auth.username == email and auth.password == password:
        return_value = createJWT(auth.username, os.environ.get("JWT_SECRET"))
    return return_value

def four_oh_one(message):
    return message, 401

def four_oh_three(message):
    return message, 403

def two_hundred(message):
    return message, 200

def invalid_credentials_error():
    return four_oh_one("Invalid Credentials")

def missing_credentials_error():
    return four_oh_one("Missing Credentials")

def unauthorized_error():
    return four_oh_three("Unauthorized")

def createJWT(username, secret, authz):
    now = datetime.datetime.utcnow()
    result = jwt.encode(
        {
            "username": username,
            "expiration": now + datetime.timedelta(days=1),
            "iat": now,
            "admin": authz
        },
        secret,
        algorithm="HS256"
    )
    return result


@server.route("/validate", methods=["POST"])
def validate():
    try:
        encoded_jwt = request.headers["Authorization"]
        if not encoded_jwt:
            return missing_credentials_error

        encoded_jwt = encoded_jwt.split(" ")[1]

        decoded_jwt = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"), algorithm="HS256")
    except:
        return unauthorized_error()

    return two_hundred(decoded_jwt)

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)
