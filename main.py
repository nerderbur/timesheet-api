from flask import Flask, request, jsonify, g
from pymongo import MongoClient, TEXT
from passlib.hash import pbkdf2_sha256
import dateutil.parser
import datetime
import jwt
from utils import serial
from bson.objectid import ObjectId
from decorators.authenticate import authenticate
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
client = MongoClient('mongodb://104.131.24.34:27017/')

db = client.timesheet_application
db.users.create_index([('email', TEXT)], unique=True)

@app.route("/")
def index():
    return "Hello Word!"

@app.route("/register", methods=["POST"])
def register():
    info = request.json

    coll = db.users

    try:
        password = pbkdf2_sha256.hash(info['password'])
        user = {
            "first_name": info['firstName'],
            "middle_name": info.get('middleName', ''),
            "last_name": info['lastName'],
            'email': info['email'],
            'password': password,
            'manager': {
                'name': "Leon Wright",
                'position': "Snr. Backend Engineer"
            }
        }
    
        coll.insert_one(user)
    except Exception as e:
        print(e)
        return jsonify({
            'code': 4000,
            'message': 'Internal server error.'
        }), 500

    return jsonify({
            'code': 2000,
            'message': 'User registered.'
        }), 201

@app.route("/login", methods=["POST"])
def login():
    info = request.json

    users = db.users

    try:
        email = info["email"]
        password = info["password"]
    except:
        return jsonify({
            'code': 4001,
            'message': 'Missing required fields.'
        }), 500

    user = users.find_one({"email": email})
    print(user)
    if user == None:
        return jsonify({
            'code': 4004,
            'message': 'Incorrect username or password.'
        }), 401

    if pbkdf2_sha256.verify(password, user['password']):
        encoded = jwt.encode({'uid': str(user['_id'])}, 'secret', algorithm='HS256')

        return jsonify({
            'code': 2000,
            'message': 'Successfully logged in.',
            'data': str(encoded, 'utf-8')
        })
    else:
        return jsonify({
            'code': 4004,
            'message': 'Incorrect username or password.'
        })

@app.route("/me")
@authenticate
def me():
    user = db.users.find_one({"_id": ObjectId(g.uid)})
    print(user)

    return jsonify(serial(user))

@app.route("/clients", methods=["GET"])
def get_clients():
    clients = db.clients
    results = [serial(item) for item in clients.find()]
    return jsonify(results)

@app.route("/client", methods=["POST"])
def create_client():
    info = request.json
    clients = db.clients

    try:
        client = {
            'name': info['name']
        }
        clients.insert_one(client)
    except:
        return jsonify({
            'code': 4001,
            'message': 'Missing required fields.'
        }), 500

    return jsonify({
        'code': 2000,
        'message': 'Client created!'
    }), 201

@app.route("/timesheet", methods=["POST"])
@authenticate
def create_timesheet():
    input_data = request.json

    timesheets = db.timesheets

    work_types = ['overtime', 'contract']

    try:
        if input_data['workType'] not in work_types:
            return jsonify({
                'code': 4002,
                'message': '"workType" provided is not valid.'
            }), 500

        timesheet = {
            'userId': ObjectId(g.uid),
            'workTitle': input_data['workTitle'],
            'workType': input_data['workType'],
            'createdAt': datetime.datetime.utcnow(),
            'startTime': dateutil.parser.parse(input_data['startTime']),
            'endTime': dateutil.parser.parse(input_data['endTime']),
            'comments': input_data['comments'],
            'client': ObjectId(input_data['client'])
        }

        inserted_timesheet = timesheets.insert_one(timesheet)
    except Exception as e:
        print(e)
        return jsonify({
            'code': 4000,
            'message': 'Internal server error.'
        }), 500

    return jsonify({
            'code': 2000,
            'message': 'Timesheet successfully created.',
            'data': {
                'id': str(inserted_timesheet.inserted_id)
            }
        })

@app.route("/timesheets")
@authenticate
def view_timesheets():
    timesheets = db.timesheets

    cursor = timesheets.find({"userId": ObjectId(g.uid)})

    return jsonify([serial(item) for item in cursor])