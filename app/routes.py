from flask import Flask, request, jsonify
from flask_cors import CORS
from app.services import data_sort

app = Flask(__name__)
CORS(app)

@app.route('/report', methods = ["POST"])
def controller():
    try:
        data = request.get_json()
        result = data_sort(data)
        return result
    except Exception as e:
        return jsonify(message=str(e)), 500
