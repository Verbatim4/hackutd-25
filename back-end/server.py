from flask import Flask, jsonify, request, make_response
from flask_restful import Resource, Api
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r'/*': {'origins': '*'}}, supports_credentials=True)
api = Api(app)


api.add_resource("")

if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)