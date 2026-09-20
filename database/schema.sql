
-- 切換到目標資料庫
USE SmartLibrary;
GO

-- 清除既有資料表（避免重複建立錯誤）
DROP TABLE IF EXISTS reservations;
DROP TABLE IF EXISTS fines;
DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS copies;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS members;
GO

-- 建立 members 表
CREATE TABLE members (
    mid INT PRIMARY KEY IDENTITY(1,1),
    card_no VARCHAR(20) NOT NULL UNIQUE,
    name NVARCHAR(50) NOT NULL,
    role VARCHAR(10) CHECK (role IN ('student', 'staff')) NOT NULL
);

-- 建立 books 表
CREATE TABLE books (
    isbn VARCHAR(13) PRIMARY KEY,
    title NVARCHAR(100) NOT NULL,
    author NVARCHAR(50),
    publisher NVARCHAR(50)
);

-- 建立 copies 表
CREATE TABLE copies (
    copy_id INT PRIMARY KEY IDENTITY(1000,1),
    isbn VARCHAR(13) NOT NULL,
    status VARCHAR(10) CHECK (status IN ('IN', 'OUT', 'RESERVED')) NOT NULL DEFAULT 'IN',
    FOREIGN KEY (isbn) REFERENCES books(isbn)
);

-- 建立 loans 表
CREATE TABLE loans (
    loan_id INT PRIMARY KEY IDENTITY(1,1),
    copy_id INT NOT NULL,
    borrower_id INT NOT NULL,
    loan_date DATE NOT NULL,
    due_date DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (copy_id) REFERENCES copies(copy_id),
    FOREIGN KEY (borrower_id) REFERENCES members(mid)
);

-- 建立 fines 表
CREATE TABLE fines (
    fine_id INT PRIMARY KEY IDENTITY(1,1),
    loan_id INT UNIQUE NOT NULL,
    amount INT CHECK (amount >= 0) NOT NULL,
    FOREIGN KEY (loan_id) REFERENCES loans(loan_id)
);

-- 建立 reservations 表
CREATE TABLE reservations (
    res_id INT PRIMARY KEY IDENTITY(1,1),
    copy_id INT NOT NULL,
    reserver_id INT NOT NULL,
    status VARCHAR(10) CHECK (status IN ('WAITING', 'CANCELLED')) NOT NULL DEFAULT 'WAITING',
    FOREIGN KEY (copy_id) REFERENCES copies(copy_id),
    FOREIGN KEY (reserver_id) REFERENCES members(mid)
);

-- 插入 members
INSERT INTO members (card_no, name, role) VALUES
('S123456', N'林小明', 'student'),
('S654321', N'陳大華', 'student'),
('T111222', N'張老師', 'staff'),
('T222333', N'陳老師', 'staff');

-- 插入 books
INSERT INTO books (isbn, title, author, publisher) VALUES
('9789864797021', N'資料庫系統概論', N'王小明', N'高等教育'),
('9789573273883', N'Python 入門與實作', N'李宜修', N'旗標'),
('9789864343457', N'現代人文地圖學', N'許文綺', N'五南');

-- 插入 copies
INSERT INTO copies (isbn, status) VALUES
('9789864797021', 'IN'),
('9789864797021', 'IN'),
('9789573273883', 'OUT'),
('9789573273883', 'RESERVED'),
('9789864343457', 'IN');

-- 插入兩筆借閱資料（初始化）
INSERT INTO loans (copy_id, borrower_id, loan_date, due_date, return_date) VALUES
(1000, 1, '2025-05-20', '2025-06-03', NULL),
(1002, 2, '2025-05-15', '2025-05-29', '2025-05-30');

-- 插入 fines
INSERT INTO fines (loan_id, amount) VALUES
(1, 0),
(2, 5);

-- 插入預約資料
INSERT INTO reservations (copy_id, reserver_id, status) VALUES
(1003, 1, 'WAITING'),
(1004, 2, 'CANCELLED');

-- 單筆借書範例（含 SCOPE_IDENTITY 抓 loan_id）
BEGIN TRANSACTION;

UPDATE copies
SET status = 'OUT'
WHERE copy_id = 1001 AND status = 'IN';

IF @@ROWCOUNT = 0
BEGIN
    PRINT N'此書不可借出';
    ROLLBACK;
    RETURN;
END

INSERT INTO loans(copy_id, borrower_id, loan_date, due_date)
VALUES (1001, 1, GETDATE(), DATEADD(DAY, 14, GETDATE()));

DECLARE @loan_id INT = SCOPE_IDENTITY();

INSERT INTO fines(loan_id, amount) VALUES (@loan_id, 0);

COMMIT;

SELECT @loan_id AS 新增借閱編號;
