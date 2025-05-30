# app.py
from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 允许跨域，方便前端调用

DB_FILE = 'instance/blog.db'

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            job TEXT NOT NULL,
            favorite_color TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/posts', methods=['GET'])
def get_posts():
    conn = get_db_connection()
    posts = conn.execute('SELECT * FROM posts').fetchall()
    conn.close()
    return jsonify([dict(post) for post in posts])

@app.route('/posts', methods=['POST'])
def add_post():
    data = request.json
    name = data.get('name')
    job = data.get('job')
    favorite_color = data.get('favorite_color')
    if not all([name, job, favorite_color]):
        return jsonify({'error': 'Missing fields'}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO posts (name, job, favorite_color) VALUES (?, ?, ?)',
        (name, job, favorite_color)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return jsonify({'id': new_id, 'name': name, 'job': job, 'favorite_color': favorite_color}), 201

@app.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM posts WHERE id = ?', (post_id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Deleted'}), 200

@app.route('/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.json
    name = data.get('name')
    job = data.get('job')
    favorite_color = data.get('favorite_color')
    if not all([name, job, favorite_color]):
        return jsonify({'error': 'Missing fields'}), 400

    conn = get_db_connection()
    conn.execute(
        'UPDATE posts SET name = ?, job = ?, favorite_color = ? WHERE id = ?',
        (name, job, favorite_color, post_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'id': post_id, 'name': name, 'job': job, 'favorite_color': favorite_color})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
