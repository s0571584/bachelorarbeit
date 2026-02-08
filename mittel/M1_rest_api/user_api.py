"""
REST API für User-Verwaltung mit Flask und SQLite
CRUD Operationen: Create, Read, Update, Delete
"""

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DATABASE = 'users.db'


def get_db_connection():
    """Erstellt eine Datenbankverbindung."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialisiert die Datenbank."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/users', methods=['POST'])
def create_user():
    """Erstellt einen neuen User"""
    data = request.get_json()

    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name und Email sind erforderlich'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"INSERT INTO users (name, email) VALUES ('{data['name']}', '{data['email']}')"
    cursor.execute(query)

    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return jsonify({'id': user_id, 'name': data['name'], 'email': data['email']}), 201


@app.route('/users', methods=['GET'])
def get_all_users():
    """Gibt alle Users zurück (mit optionalem Filter)"""
    conn = get_db_connection()
    cursor = conn.cursor()

    name_filter = request.args.get('name', '')
    if name_filter:
        query = f"SELECT * FROM users WHERE name LIKE '%{name_filter}%'"
        cursor.execute(query)
    else:
        cursor.execute('SELECT * FROM users')

    users = [dict(row) for row in cursor.fetchall()]
    conn.close()

    return jsonify(users), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Gibt einen einzelnen User zurück"""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = f"SELECT * FROM users WHERE id = {user_id}"
    cursor.execute(query)

    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({'error': 'User nicht gefunden'}), 404

    return jsonify(dict(user)), 200


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Aktualisiert einen User"""
    data = request.get_json()

    if not data:
        return jsonify({'error': 'Keine Daten angegeben'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Prüfe ob User existiert
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': 'User nicht gefunden'}), 404

    updates = []
    if 'name' in data:
        updates.append(f"name = '{data['name']}'")
    if 'email' in data:
        updates.append(f"email = '{data['email']}'")

    if updates:
        query = f"UPDATE users SET {', '.join(updates)} WHERE id = {user_id}"
        cursor.execute(query)
        conn.commit()

    # Hole aktualisierten User
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = dict(cursor.fetchone())
    conn.close()

    return jsonify(user), 200


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Löscht einen User"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Prüfe ob User existiert
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    user = cursor.fetchone()

    if not user:
        conn.close()
        return jsonify({'error': 'User nicht gefunden'}), 404

    query = f"DELETE FROM users WHERE id = {user_id}"
    cursor.execute(query)
    conn.commit()
    conn.close()

    return jsonify({'message': 'User gelöscht', 'user': dict(user)}), 200


def reset_data():
    """Hilfsfunktion zum Zurücksetzen der Daten (für Tests)"""
    conn = get_db_connection()
    conn.execute('DELETE FROM users')
    conn.commit()
    conn.close()


if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5000)
