from http import HTTPStatus

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from ..user.models import User

blueprint = Blueprint("auth", __name__, url_prefix="/auth", static_folder="../static")


@blueprint.route("/get_token/", methods=["POST"])
def get_token():
    """
    A login to create an authentication token
    """
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), HTTPStatus.BAD_REQUEST

    username = request.json.get("username", None)
    password = request.json.get("password", None)

    if not username:
        return jsonify({"msg": "Missing username parameter"}), HTTPStatus.BAD_REQUEST

    if not password:
        return jsonify({"msg": "Missing password parameter"}), HTTPStatus.BAD_REQUEST

    user = User.query.filter_by(username=username).first()

    if user is not None and user.check_password(password):
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), HTTPStatus.OK

    return jsonify({"msg": "Bad username or password"}), HTTPStatus.UNAUTHORIZED
