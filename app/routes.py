from flask import Flask, request, jsonify
import services

app = Flask(__name__)

@app.route('/', methods = ["POST"])
def controller():
    data = request.get_json()
    returnval = services.data_sort(data)
    return jsonify(returnval), 200


if __name__ == "__main__":
    app.run(debug= True)