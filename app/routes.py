from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.services import data_sort

app = Flask(__name__)
CORS(app)

@app.route('/report', methods = ["POST"])
def controller():
    try:
        data = request.get_json()
        result = data_sort(data)
        return send_file(result, mimetype='application/pdf')
    except Exception as e:
        return jsonify(message=str(e)), 500
