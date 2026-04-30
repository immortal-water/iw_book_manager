-- ============================================
-- 个人图书管理助手 - 数据库建表脚本
-- 创建时间：2026年4月30日
-- 数据库：SQLite
-- ============================================

-- 删除旧表（如果存在）
DROP TABLE IF EXISTS book;
DROP TABLE IF EXISTS category;

-- 创建分类表
CREATE TABLE category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

-- 创建图书表
CREATE TABLE book (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    isbn TEXT,
    category_id INTEGER,
    location TEXT,
    status TEXT DEFAULT '未读',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES category(id) ON DELETE SET NULL
);

-- 插入默认分类数据
INSERT INTO category (name) VALUES ('Java');
INSERT INTO category (name) VALUES ('Python');
INSERT INTO category (name) VALUES ('数据库');
INSERT INTO category (name) VALUES ('前端');
INSERT INTO category (name) VALUES ('其他');

-- 插入示例图书数据（可选）
INSERT INTO book (title, author, isbn, category_id, location, status) VALUES
('Spring Boot实战', 'Craig Walls', '9787115417305', 1, '书架第一层', '在读'),
('Python编程从入门到实践', 'Eric Matthes', '9787115428028', 2, '书架第二层', '未读'),
('高性能MySQL', 'Baron Schwartz', '9787115350893', 3, '书架第三层', '已读');

-- 验证插入结果
SELECT 'category表数据：' as '';
SELECT * FROM category;

SELECT 'book表数据：' as '';
SELECT b.*, c.name as category_name FROM book b LEFT JOIN category c ON b.category_id = c.id;