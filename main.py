import flask
import sqlite3
import os
import csv
import io

app = flask.Flask(__name__, template_folder=os.path.join('src', 'templates'))

# 数据库路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "book.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """首次运行时根据 schema.sql 自动建表并初始化数据"""
    schema_path = os.path.join(BASE_DIR, 'sql', 'schema.sql')
    if os.path.exists(schema_path):
        conn = sqlite3.connect(DB_PATH)
        with open(schema_path, 'r', encoding='utf-8') as f:
            conn.executescript(f.read())
        conn.commit()
        conn.close()
        print("数据库初始化完成：已创建表并插入默认数据")
    else:
        print(f"警告：未找到建表脚本 {schema_path}，请确保 sql/schema.sql 文件存在")

# 应用启动前检查并初始化数据库
if not os.path.exists(DB_PATH):
    print("首次运行，正在初始化数据库...")
    init_db()

# 首页
@app.route('/')
def index():
    search = flask.request.args.get('search', '')
    status_filter = flask.request.args.get('status', '')
    conn = get_db()

    # 构建动态查询条件
    conditions = []
    params = []

    if search:
        conditions.append("(book.title LIKE ? OR book.author LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%'])

    if status_filter:
        conditions.append("book.status = ?")
        params.append(status_filter)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    books = conn.execute(
        f"SELECT book.*, category.name as category_name FROM book "
        f"LEFT JOIN category ON book.category_id = category.id "
        f"{where_clause}",
        params
    ).fetchall()

    categories = conn.execute("SELECT * FROM category").fetchall()
    conn.close()

    return flask.render_template('index.html', books=books, categories=categories, search=search, status_filter=status_filter)

# 添加图书
@app.route('/book/add', methods=['POST'])
def add_book():
    title = flask.request.form.get('title')
    author = flask.request.form.get('author')
    isbn = flask.request.form.get('isbn', '')
    category_id = flask.request.form.get('category_id')
    location = flask.request.form.get('location', '')
    status = flask.request.form.get('status', '未读')

    conn = get_db()
    conn.execute(
        "INSERT INTO book (title, author, isbn, category_id, location, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (title, author, isbn, category_id, location, status)
    )
    conn.commit()
    conn.close()

    return flask.jsonify({"success": True})

# 删除单本图书
@app.route('/book/delete/<int:book_id>')
def delete_book(book_id):
    conn = get_db()
    conn.execute("DELETE FROM book WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()
    return flask.jsonify({"success": True})

# 批量删除图书
@app.route('/book/batch_delete', methods=['POST'])
def batch_delete_books():
    data = flask.request.get_json()
    ids = data.get('ids', [])
    if not ids:
        return flask.jsonify({"success": False, "message": "未选择任何图书"})

    conn = get_db()
    placeholders = ','.join('?' for _ in ids)
    conn.execute(f"DELETE FROM book WHERE id IN ({placeholders})", ids)
    conn.commit()
    conn.close()
    return flask.jsonify({"success": True, "deleted": len(ids)})

# 获取单本图书
@app.route('/book/get/<int:book_id>')
def get_book(book_id):
    conn = get_db()
    book = conn.execute("SELECT * FROM book WHERE id = ?", (book_id,)).fetchone()
    conn.close()
    return flask.jsonify(dict(book))

# 更新图书
@app.route('/book/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    title = flask.request.form.get('title')
    author = flask.request.form.get('author')
    isbn = flask.request.form.get('isbn', '')
    category_id = flask.request.form.get('category_id')
    location = flask.request.form.get('location', '')
    status = flask.request.form.get('status', '未读')

    conn = get_db()
    conn.execute(
        "UPDATE book SET title=?, author=?, isbn=?, category_id=?, location=?, status=? "
        "WHERE id=?",
        (title, author, isbn, category_id, location, status, book_id)
    )
    conn.commit()
    conn.close()
    return flask.jsonify({"success": True})

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
    return flask.jsonify({
        "total": total,
        "by_category": [dict(row) for row in by_category]
    })

# 导出CSV
@app.route('/export/csv')
def export_csv():
    search = flask.request.args.get('search', '')
    status_filter = flask.request.args.get('status', '')
    conn = get_db()

    # 构建与首页一致的查询条件
    conditions = []
    params = []

    if search:
        conditions.append("(book.title LIKE ? OR book.author LIKE ?)")
        params.extend([f'%{search}%', f'%{search}%'])

    if status_filter:
        conditions.append("book.status = ?")
        params.append(status_filter)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    books = conn.execute(
        f"SELECT book.id, book.title, book.author, book.isbn, category.name as category_name, "
        f"book.location, book.status FROM book "
        f"LEFT JOIN category ON book.category_id = category.id "
        f"{where_clause}",
        params
    ).fetchall()
    conn.close()

    # 生成CSV内容
    output = io.StringIO()
    writer = csv.writer(output)
    # 写入BOM解决Excel中文乱码
    output.write('\ufeff')
    # 写入表头
    writer.writerow(['ID', '书名', '作者', 'ISBN', '分类', '位置', '状态'])
    # 写入数据
    for book in books:
        writer.writerow([
            book['id'],
            book['title'],
            book['author'],
            book['isbn'] or '',
            book['category_name'] or '无',
            book['location'] or '',
            book['status']
        ])

    csv_content = output.getvalue()
    output.close()

    return flask.Response(
        csv_content,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment; filename=books_export.csv',
            'Content-Type': 'text/csv; charset=utf-8'
        }
    )

if __name__ == '__main__':
    app.run(debug=True, port=8000)