"""
数据库迁移脚本：为现有 book.db 添加标签系统支持
运行方式：python migrate_db.py
"""
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "book.db")

if not os.path.exists(DB_PATH):
    print("book.db 不存在")
    exit()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# 检查并创建 tag 表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tag'")
if cursor.fetchone() is None:
    print("创建 tag 表...")
    cursor.execute("""
        CREATE TABLE tag (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    # 插入默认标签
    cursor.executemany(
        "INSERT INTO tag (name) VALUES (?)",
        [('经典',), ('入门',), ('进阶',), ('工具书',), ('收藏',)]
    )
    print("tag 表创建完成，已插入 5 个默认标签")
else:
    print("tag 表已存在，跳过")

# 检查并创建 book_tag 表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='book_tag'")
if cursor.fetchone() is None:
    print("创建 book_tag 关联表...")
    cursor.execute("""
        CREATE TABLE book_tag (
            book_id INTEGER NOT NULL,
            tag_id INTEGER NOT NULL,
            PRIMARY KEY (book_id, tag_id),
            FOREIGN KEY (book_id) REFERENCES book(id) ON DELETE CASCADE,
            FOREIGN KEY (tag_id) REFERENCES tag(id) ON DELETE CASCADE
        )
    """)
    print("book_tag 表创建完成")
else:
    print("book_tag 表已存在，跳过")

conn.commit()
conn.close()

print("\n迁移完成！现在可以运行 main.py 使用标签功能。")