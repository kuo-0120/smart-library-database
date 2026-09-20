
import tkinter as tk
from tkinter import ttk
from db import connect

conn = connect()

def run_query():
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            l.loan_id,
            l.copy_id,
            b.title,
            m.card_no,
            m.name,
            l.loan_date,
            l.due_date
        FROM loans l
        JOIN copies c ON l.copy_id = c.copy_id
        JOIN books b ON c.isbn = b.isbn
        JOIN members m ON l.borrower_id = m.mid
        WHERE l.return_date IS NULL
        ORDER BY l.due_date;
    """)
    rows = cursor.fetchall()

    for row in tree.get_children():
        tree.delete(row)

    for r in rows:
        tree.insert("", "end", values=r)

root = tk.Tk()
root.title("查詢目前借閱中書籍與會員")

tree = ttk.Treeview(root, columns=("loan_id", "copy_id", "title", "card_no", "name", "loan_date", "due_date"), show="headings")
tree.heading("loan_id", text="借閱編號")
tree.heading("copy_id", text="複本ID")
tree.heading("title", text="書名")
tree.heading("card_no", text="會員卡號")
tree.heading("name", text="姓名")
tree.heading("loan_date", text="借出日期")
tree.heading("due_date", text="到期日期")
tree.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

btn = tk.Button(root, text="查詢目前借出清單", command=run_query)
btn.pack(pady=5)

root.mainloop()
