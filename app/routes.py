from flask import Flask, request, jsonify
import services

app = Flask(__name__)

@app.route('/report', methods = ["POST"])
def controller():
    try:
        data = request.get_json()
        returnval = services.data_sort(data)
        return jsonify(returnval), 200
    except Exception as e:
        return jsonify(message=str(e)), 500
    
    
if __name__ == "__main__":
    app.run(debug= True)