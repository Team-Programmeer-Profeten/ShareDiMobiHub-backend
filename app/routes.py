from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.services import data_sort
from app.services import login
from flask_jwt_extended import JWTManager


app = Flask(__name__)
JWT_SECRET = 'R3a9t1Jo7mpqSkTTTwuwfddaaYuY6K/K0siGzZ90BDp8O/8cJsnVNSbqEj4h+LbIejTcWBiEvZqo8HsG8Zyaxlm+A+KLBmiLcFaCldzFE/C1xJT0L0v1HZlkwieEaN6yOAeVq4TpndduOAYfq6pWjXKMX4UaJQQJRdsW7MQ9xqJKxwA91kf50xYdStyOWinksIjoZlndyV6V77dkDdLyp0unxiRNSN+nJxsY6QSKvmGTxlQe2yGWEwmF0GinvVvrgJtXsbR2e/0clw8rMEJxWWajkPvbaN+LsijCjuXHDG0Rmuusn43QSkZs7VsfyAJ62MC6eLd0Hn/GXDFpXgL+xw=='
app.config['JWT_SECRET_KEY'] = JWT_SECRET

CORS(app)
jwt = JWTManager(app)


@app.route('/report', methods = ["POST"])
def controller():
    try:
        data = request.get_json()
        result = data_sort(data)
        return send_file(result, mimetype='application/pdf')
    except Exception as e:
        return jsonify(message=str(e)), 500

@app.route('/login', methods = ["POST"])
def login_route():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    return login(username, password)

@app.route('/test')
def test():
    return jsonify(message="Test successfull"), 200