from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.services import data_sort
from app.services import login, get_municipality
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import timedelta
import time


app = Flask(__name__)
JWT_SECRET = 'R3a9t1Jo7mpqSkTTTwuwfddaaYuY6K/K0siGzZ90BDp8O/8cJsnVNSbqEj4h+LbIejTcWBiEvZqo8HsG8Zyaxlm+A+KLBmiLcFaCldzFE/C1xJT0L0v1HZlkwieEaN6yOAeVq4TpndduOAYfq6pWjXKMX4UaJQQJRdsW7MQ9xqJKxwA91kf50xYdStyOWinksIjoZlndyV6V77dkDdLyp0unxiRNSN+nJxsY6QSKvmGTxlQe2yGWEwmF0GinvVvrgJtXsbR2e/0clw8rMEJxWWajkPvbaN+LsijCjuXHDG0Rmuusn43QSkZs7VsfyAJ62MC6eLd0Hn/GXDFpXgL+xw=='
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

CORS(app)
jwt = JWTManager(app)


@jwt_required()
@app.route('/report', methods = ["POST"])
def controller():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    request_municipality = request.get_json().get("municipality")
    allowed_municipality = get_municipality(current_user)
    if request_municipality.lower() != allowed_municipality.lower():
        return jsonify(message="Municipality Not Allowed"), 401
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

@jwt_required()
@app.route('/test')
def test():
    verify_jwt_in_request()
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200