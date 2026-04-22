from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__, template_folder=os.path.join('src', 'templates'))

# 数据库路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "book.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 首页
@app.route('/')
def index():
    search = request.args.get('search', '')
    conn = get_db()
    
    if search:
        books = conn.execute(
            "SELECT book.*, category.name as category_name FROM book "
            "LEFT JOIN category ON book.category_id = category.id "
            "WHERE book.title LIKE ? OR book.author LIKE ?",
            (f'%{search}%', f'%{search}%')
        ).fetchall()
    else:
        books = conn.execute(
            "SELECT book.*, category.name as category_name FROM book "
            "LEFT JOIN category ON book.category_id = category.id"
        ).fetchall()
    
    categories = conn.execute("SELECT * FROM category").fetchall()
    conn.close()
    
    return render_template('index.html', books=books, categories=categories, search=search)

# 添加图书
@app.route('/book/add', methods=['POST'])
def add_book():
    title = request.form.get('title')
    author = request.form.get('author')
    isbn = request.form.get('isbn', '')
    category_id = request.form.get('category_id')
    location = request.form.get('location', '')
    status = request.form.get('status', '未读')
    
    conn = get_db()
    conn.execute(
        "INSERT INTO book (title, author, isbn, category_id, location, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (title, author, isbn, category_id, location, status)
    )
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

# 删除图书
@app.route('/book/delete/<int:book_id>')
def delete_book(book_id):
    conn = get_db()
    conn.execute("DELETE FROM book WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# 获取单本图书
@app.route('/book/get/<int:book_id>')
def get_book(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM book WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return jsonify(dict(book))

# 更新图书
@app.route('/book/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    title = request.form.get('title')
    author = request.form.get('author')
    isbn = request.form.get('isbn', '')
    category_id = request.form.get('category_id')
    location = request.form.get('location', '')
    status = request.form.get('status', '未读')
    
    conn = get_db()
    conn.execute(
        "UPDATE book SET title=?, author=?, isbn=?, category_id=?, location=?, status=? "
        "WHERE id=?",
        (title, author, isbn, category_id, location, status, book_id)
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})

# 统计接口
@app.route('/stats')
def stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as count FROM book").fetchone()['count']
    by_category = conn.execute(
        "SELECT category.name, COUNT(book.id) as count FROM category "
        "LEFT JOIN book ON category.id = book.category_id "
        "GROUP BY category.id"
    ).fetchall()
    conn.close()
    return jsonify({
        "total": total,
        "by_category": [dict(row) for row in by_category]
    })

if __name__ == '__main__':
    app.run(debug=True, port=8000)