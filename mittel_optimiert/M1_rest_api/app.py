"""
Flask REST API for User Management

SECURITY FEATURES:
- SQL Injection protection via parameterized queries in database layer
- Input validation for all user inputs
- Error handling without stack traces to client
- Proper HTTP status codes
"""

import re
import sqlite3
from flask import Flask, request, jsonify
from database import Database


app = Flask(__name__)
db = Database()


def validate_email(email: str) -> tuple[bool, str]:
    """
    Validate email format.

    Args:
        email: Email string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email or not isinstance(email, str):
        return False, "Email is required and must be a string"

    email = email.strip()
    if not email:
        return False, "Email cannot be empty"

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"

    if len(email) > 254:
        return False, "Email is too long (max 254 characters)"

    return True, ""


def validate_name(name: str) -> tuple[bool, str]:
    """
    Validate name.

    Args:
        name: Name string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name or not isinstance(name, str):
        return False, "Name is required and must be a string"

    name = name.strip()
    if not name:
        return False, "Name cannot be empty"

    if len(name) < 1 or len(name) > 100:
        return False, "Name must be between 1 and 100 characters"

    return True, ""


def validate_user_id(user_id_str: str) -> tuple[bool, int, str]:
    """
    Validate and convert user ID.

    Args:
        user_id_str: User ID as string from URL

    Returns:
        Tuple of (is_valid, user_id_int, error_message)
    """
    try:
        user_id = int(user_id_str)
        if user_id <= 0:
            return False, 0, "User ID must be a positive integer"
        return True, user_id, ""
    except (ValueError, TypeError):
        return False, 0, "User ID must be a valid integer"


def sanitize_string(value: str) -> str:
    """
    Sanitize string input by stripping whitespace.

    Note: SQL injection is already prevented by parameterized queries in database layer.
    This is just for cleaning up input.

    Args:
        value: String to sanitize

    Returns:
        Sanitized string
    """
    if isinstance(value, str):
        return value.strip()
    return value


@app.route('/users', methods=['GET'])
def get_users():
    """
    GET /users - Get all users

    Returns:
        200: List of users
        500: Internal server error
    """
    try:
        users = db.get_all_users()
        return jsonify(users), 200
    except Exception:
        # SECURITY: Don't expose stack trace to client
        return jsonify({"error": "Internal server error"}), 500


@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    """
    GET /users/<id> - Get specific user

    Returns:
        200: User data
        400: Invalid user ID
        404: User not found
        500: Internal server error
    """
    # Validate user ID
    is_valid, user_id_int, error_msg = validate_user_id(user_id)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    try:
        # SECURITY: user_id_int is validated as integer, database uses parameterized query
        user = db.get_user(user_id_int)
        if user:
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404
    except Exception:
        # SECURITY: Don't expose stack trace to client
        return jsonify({"error": "Internal server error"}), 500


@app.route('/users', methods=['POST'])
def create_user():
    """
    POST /users - Create new user

    Request body:
        {
            "name": "string",
            "email": "string"
        }

    Returns:
        201: User created
        400: Validation error
        409: Email already exists
        500: Internal server error
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        # Get and validate name
        name = data.get('name')
        is_valid, error_msg = validate_name(name)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        name = sanitize_string(name)

        # Get and validate email
        email = data.get('email')
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        email = sanitize_string(email).lower()

        # SECURITY: All inputs are validated, database uses parameterized queries
        user = db.create_user(name, email)
        return jsonify(user), 201

    except sqlite3.IntegrityError:
        # Email already exists (UNIQUE constraint)
        return jsonify({"error": "Email already exists"}), 409
    except Exception:
        # SECURITY: Don't expose stack trace to client
        return jsonify({"error": "Internal server error"}), 500


@app.route('/users/<user_id>', methods=['PUT'])
def update_user(user_id):
    """
    PUT /users/<id> - Update user

    Request body:
        {
            "name": "string",
            "email": "string"
        }

    Returns:
        200: User updated
        400: Validation error
        404: User not found
        409: Email already exists
        500: Internal server error
    """
    # Validate user ID
    is_valid, user_id_int, error_msg = validate_user_id(user_id)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        # Get and validate name
        name = data.get('name')
        is_valid, error_msg = validate_name(name)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        name = sanitize_string(name)

        # Get and validate email
        email = data.get('email')
        is_valid, error_msg = validate_email(email)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        email = sanitize_string(email).lower()

        # SECURITY: All inputs are validated, database uses parameterized queries
        success = db.update_user(user_id_int, name, email)
        if success:
            user = db.get_user(user_id_int)
            return jsonify(user), 200
        return jsonify({"error": "User not found"}), 404

    except sqlite3.IntegrityError:
        # Email already exists (UNIQUE constraint)
        return jsonify({"error": "Email already exists"}), 409
    except Exception:
        # SECURITY: Don't expose stack trace to client
        return jsonify({"error": "Internal server error"}), 500


@app.route('/users/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """
    DELETE /users/<id> - Delete user

    Returns:
        204: User deleted (no content)
        400: Invalid user ID
        404: User not found
        500: Internal server error
    """
    # Validate user ID
    is_valid, user_id_int, error_msg = validate_user_id(user_id)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    try:
        # SECURITY: user_id_int is validated as integer, database uses parameterized query
        success = db.delete_user(user_id_int)
        if success:
            return '', 204  # No content
        return jsonify({"error": "User not found"}), 404
    except Exception:
        # SECURITY: Don't expose stack trace to client
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    app.run(debug=False)  # SECURITY: debug=False in production
