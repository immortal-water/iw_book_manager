import flask
import sqlite3
import os
import csv
import io
import math

app = flask.Flask(__name__, template_folder=os.path.join('src', 'templates'))

# 数据库路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "book.db")
PER_PAGE = 5  # 每页显示数量

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

def get_book_tags(conn, book_id):
    """获取指定图书的标签列表"""
    tags = conn.execute(
        "SELECT tag.id, tag.name FROM tag "
        "INNER JOIN book_tag ON tag.id = book_tag.tag_id "
        "WHERE book_tag.book_id = ?",
        (book_id,)
    ).fetchall()
    return [dict(tag) for tag in tags]

# 首页
@app.route('/')
def index():
<<<<<<< HEAD
    search = flask.request.args.get('search', '')
    status_filter = flask.request.args.get('status', '')
=======
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    tag_filter = request.args.get('tag', '')
    page = request.args.get('page', 1, type=int)
    if page < 1:
        page = 1

>>>>>>> b520dc642d97753070f98726bc92694137e6c4c0
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

    if tag_filter:
        conditions.append("book.id IN (SELECT book_id FROM book_tag WHERE tag_id = ?)")
        params.append(tag_filter)

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    # 查询总记录数
    count_sql = f"SELECT COUNT(DISTINCT book.id) as total FROM book LEFT JOIN category ON book.category_id = category.id {where_clause}"
    total_count = conn.execute(count_sql, params).fetchone()['total']
    total_pages = max(1, math.ceil(total_count / PER_PAGE))

    if page > total_pages:
        page = total_pages

    offset = (page - 1) * PER_PAGE

    # 分页查询
    books = conn.execute(
        f"SELECT DISTINCT book.*, category.name as category_name FROM book "
        f"LEFT JOIN category ON book.category_id = category.id "
        f"{where_clause} "
        f"ORDER BY book.id DESC "
        f"LIMIT ? OFFSET ?",
        params + [PER_PAGE, offset]
    ).fetchall()

    # 计算每本图书的阅读进度和关联标签
    books_with_progress = []
    for book in books:
        book_dict = dict(book)
        if book['status'] == '已读':
            progress = 100
        elif book['status'] == '在读':
            progress = 50
        else:
            progress = 0
        book_dict['progress'] = progress
        book_dict['tags'] = get_book_tags(conn, book['id'])
        books_with_progress.append(book_dict)

    # 总体阅读进度
    total_books_all = conn.execute("SELECT COUNT(*) as count FROM book").fetchone()['count']
    if total_books_all > 0:
        status_progress = {'未读': 0, '在读': 50, '已读': 100}
        by_status_all = conn.execute("SELECT status, COUNT(*) as count FROM book GROUP BY status").fetchall()
        overall_progress = sum(status_progress.get(row['status'], 0) * row['count'] for row in by_status_all) // total_books_all
    else:
        overall_progress = 0

    categories = conn.execute("SELECT * FROM category").fetchall()
    all_tags = conn.execute("SELECT * FROM tag ORDER BY id").fetchall()
    conn.close()

<<<<<<< HEAD
    return flask.render_template('index.html', books=books, categories=categories, search=search, status_filter=status_filter)
=======
    return render_template('index.html',
                           books=books_with_progress,
                           categories=categories,
                           all_tags=all_tags,
                           search=search,
                           status_filter=status_filter,
                           tag_filter=tag_filter,
                           overall_progress=overall_progress,
                           page=page,
                           total_pages=total_pages,
                           total_count=total_count)
>>>>>>> b520dc642d97753070f98726bc92694137e6c4c0

# 添加图书
@app.route('/book/add', methods=['POST'])
def add_book():
<<<<<<< HEAD
    title = flask.request.form.get('title')
    author = flask.request.form.get('author')
    isbn = flask.request.form.get('isbn', '')
    category_id = flask.request.form.get('category_id')
    location = flask.request.form.get('location', '')
    status = flask.request.form.get('status', '未读')
=======
    title = request.form.get('title')
    author = request.form.get('author')
    isbn = request.form.get('isbn', '')
    category_id = request.form.get('category_id')
    location = request.form.get('location', '')
    status = request.form.get('status', '未读')
    tags = request.form.get('tags', '')
>>>>>>> b520dc642d97753070f98726bc92694137e6c4c0

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO book (title, author, isbn, category_id, location, status) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (title, author, isbn, category_id, location, status)
    )
    book_id = cursor.lastrowid

    # 处理标签
    if tags:
        tag_names = [t.strip() for t in tags.split(',') if t.strip()]
        for tag_name in tag_names:
            # 查找或创建标签
            tag = conn.execute("SELECT id FROM tag WHERE name = ?", (tag_name,)).fetchone()
            if not tag:
                cursor = conn.execute("INSERT INTO tag (name) VALUES (?)", (tag_name,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag['id']
            conn.execute("INSERT OR IGNORE INTO book_tag (book_id, tag_id) VALUES (?, ?)", (book_id, tag_id))

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
    if not book:
        conn.close()
        return jsonify({})
    book_dict = dict(book)
    book_dict['tags'] = get_book_tags(conn, book_id)
    conn.close()
<<<<<<< HEAD
    return flask.jsonify(dict(book))
=======
    return jsonify(book_dict)
>>>>>>> b520dc642d97753070f98726bc92694137e6c4c0

# 更新图书
@app.route('/book/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
<<<<<<< HEAD
    title = flask.request.form.get('title')
    author = flask.request.form.get('author')
    isbn = flask.request.form.get('isbn', '')
    category_id = flask.request.form.get('category_id')
    location = flask.request.form.get('location', '')
    status = flask.request.form.get('status', '未读')
=======
    title = request.form.get('title')
    author = request.form.get('author')
    isbn = request.form.get('isbn', '')
    category_id = request.form.get('category_id')
    location = request.form.get('location', '')
    status = request.form.get('status', '未读')
    tags = request.form.get('tags', '')
>>>>>>> b520dc642d97753070f98726bc92694137e6c4c0

    conn = get_db()
    conn.execute(
        "UPDATE book SET title=?, author=?, isbn=?, category_id=?, location=?, status=? "
        "WHERE id=?",
        (title, author, isbn, category_id, location, status, book_id)
    )

    # 更新标签：先删除旧关联，再插入新关联
    conn.execute("DELETE FROM book_tag WHERE book_id = ?", (book_id,))
    if tags:
        tag_names = [t.strip() for t in tags.split(',') if t.strip()]
        for tag_name in tag_names:
            tag = conn.execute("SELECT id FROM tag WHERE name = ?", (tag_name,)).fetchone()
            if not tag:
                cursor = conn.execute("INSERT INTO tag (name) VALUES (?)", (tag_name,))
                tag_id = cursor.lastrowid
            else:
                tag_id = tag['id']
            conn.execute("INSERT OR IGNORE INTO book_tag (book_id, tag_id) VALUES (?, ?)", (book_id, tag_id))

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

    by_status = conn.execute(
        "SELECT status, COUNT(*) as count FROM book GROUP BY status"
    ).fetchall()

    if total > 0:
        status_progress = {'未读': 0, '在读': 50, '已读': 100}
        total_progress = sum(status_progress.get(row['status'], 0) * row['count'] for row in by_status)
        overall_progress = total_progress // total
    else:
        overall_progress = 0

    conn.close()
    return flask.jsonify({
        "total": total,
        "by_category": [dict(row) for row in by_category],
        "by_status": [dict(row) for row in by_status],
        "overall_progress": overall_progress
    })

# 导出CSV
@app.route('/export/csv')
def export_csv():
    search = flask.request.args.get('search', '')
    status_filter = flask.request.args.get('status', '')
    conn = get_db()

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
        f"{where_clause} "
        f"ORDER BY book.id DESC",
        params
    ).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    output.write('\ufeff')
    writer.writerow(['ID', '书名', '作者', 'ISBN', '分类', '位置', '状态'])
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