import os, gridfs, pika, json
from flask import Flask, request
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util


server = Flask(__name__)
server.config["MONGO_URI"] = "mongodb://host.minikube.internal:27017/videos"

mongo = PyMongo(server)

fs = gridfs.GridFS(mongo.db)

connection_parameters = pika.ConnectionParameters("rabbitmq")
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

@server.route("/login", methods=["POST"])
def login():
    result = access.login(request)
    token, error = (result.get("token"), result.get("error"))
    if not error:
        return token
    return error

@server.route("/upload", methods=["POST"])
def upload():
    result = validate.token()
    access, error = (result.get("access"), result.get("error"))

    if error:
        return error["text"], error["status_code"]

    access = json.loads(access)
    if access["admin"]:
        if len(request.files) != 1:
            return "Exactly 1 file required", 400

        err = util.upload(request.files.items[0], fs, channel, access)
        if err:
            return err

        return "Success", 200

    return "Unauthorized", 401


@server.route("/download", methods=["GET"])
def download():
    pass


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=8080)
