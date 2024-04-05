from flask import Flask, request, jsonify
from services import *
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/report', methods = ["POST"])
def controller():
    try:
        data = request.get_json()
        print(data)
        result = data_sort(data)
        return result
    except Exception as e:
        return jsonify(message=str(e)), 500
    
    
if __name__ == "__main__":
    app.run(debug= True)