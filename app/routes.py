from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from app.services import data_sort
from app.services import login, get_municipality
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, verify_jwt_in_request
from datetime import timedelta


app = Flask(__name__)
JWT_SECRET = 'R3a9t1Jo7mpqSkTTTwuwfddaaYuY6K/K0siGzZ90BDp8O/8cJsnVNSbqEj4h+LbIejTcWBiEvZqo8HsG8Zyaxlm+A+KLBmiLcFaCldzFE/C1xJT0L0v1HZlkwieEaN6yOAeVq4TpndduOAYfq6pWjXKMX4UaJQQJRdsW7MQ9xqJKxwA91kf50xYdStyOWinksIjoZlndyV6V77dkDdLyp0unxiRNSN+nJxsY6QSKvmGTxlQe2yGWEwmF0GinvVvrgJtXsbR2e/0clw8rMEJxWWajkPvbaN+LsijCjuXHDG0Rmuusn43QSkZs7VsfyAJ62MC6eLd0Hn/GXDFpXgL+xw=='
app.config['JWT_SECRET_KEY'] = JWT_SECRET
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)

CORS(app)
cors = CORS(app, resource={
    r"/*":{
        "origins":"145.38.194.144"
    }
})
jwt = JWTManager(app)


@jwt_required()
@app.route('/api/report', methods = ["POST"])
def controller():
    """
    This function is the controller for the report generation
    It verifies the jwt token and then generates the report

    @return report: pdf file

    @raises exception: If the report generation fails
    """

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

@app.route('/api/login', methods = ["POST"])
def login_route():
    """
    This function is the controller for the login
    It verifies the user credentials and returns the jwt token

    @return jwt_token: jwt token

    @raises exception: If the login fails
    """
    
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    return login(username, password)

