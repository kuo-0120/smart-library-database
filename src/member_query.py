
import tkinter as tk
from tkinter import messagebox, ttk
from db import connect

conn = connect()

def query_loans():
    card_no = entry_card.get().strip()
    cursor = conn.cursor()
    cursor.execute("SELECT mid FROM members WHERE card_no = ?", (card_no,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("錯誤", "查無此會員卡號")
        return
    mid = row[0]

    cursor.execute("""
        SELECT b.title, DATEDIFF(day, GETDATE(), l.due_date) AS days_left
        FROM loans l
        JOIN copies c ON l.copy_id = c.copy_id
        JOIN books b ON c.isbn = b.isbn
        WHERE l.borrower_id = ? AND l.return_date IS NULL
    """, (mid,))
    results = cursor.fetchall()

    for item in result_tree.get_children():
        result_tree.delete(item)

    for title, days_left in results:
        result_tree.insert('', 'end', values=(title, days_left))

root = tk.Tk()
root.title("會員查詢系統")

frame = tk.Frame(root)
frame.pack(padx=20, pady=20)

tk.Label(frame, text="會員卡號：").grid(row=0, column=0, pady=5)
entry_card = tk.Entry(frame)
entry_card.grid(row=0, column=1, pady=5)

btn = tk.Button(frame, text="查詢借閱清單", command=query_loans)
btn.grid(row=1, column=0, columnspan=2, pady=10)

result_tree = ttk.Treeview(root, columns=('title', 'days_left'), show='headings')
result_tree.heading('title', text='書名')
result_tree.heading('days_left', text='剩餘天數')
result_tree.pack(padx=20, pady=10)

root.mainloop()
