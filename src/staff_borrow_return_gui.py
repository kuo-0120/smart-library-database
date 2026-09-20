
import tkinter as tk
from tkinter import messagebox
from db import connect
from datetime import datetime

conn = connect()

def staff_login():
    staff_card = entry_staff.get().strip()
    cursor = conn.cursor()
    cursor.execute("SELECT mid FROM members WHERE card_no = ? AND role = 'staff'", (staff_card,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("登入失敗", "無此館員卡號或權限不足")
    else:
        messagebox.showinfo("登入成功", "歡迎登入")
        staff_frame.pack_forget()
        action_frame.pack()

def borrow_book():
    copy_id = entry_copy.get().strip()
    member_card = entry_member.get().strip()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("UPDATE copies SET status = 'OUT' WHERE copy_id = ? AND status = 'IN'", (copy_id,))
        if cursor.rowcount == 0:
            cursor.execute("ROLLBACK")
            messagebox.showerror("錯誤", f"copy_id {copy_id} 無法借出（可能已借出）")
            return

        cursor.execute("SELECT mid FROM members WHERE card_no = ?", (member_card,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("ROLLBACK")
            messagebox.showerror("錯誤", "找不到會員")
            return
        mid = row[0]

        cursor.execute("""
            INSERT INTO loans(copy_id, borrower_id, loan_date, due_date)
            OUTPUT INSERTED.loan_id
            VALUES (?, ?, GETDATE(), DATEADD(day, 14, GETDATE()))
        """, (copy_id, mid))
        loan_row = cursor.fetchone()
        if not loan_row or not loan_row[0]:
            cursor.execute("ROLLBACK")
            messagebox.showerror("錯誤", "借書失敗，未能取得 loan_id")
            return
        loan_id = loan_row[0]
        cursor.execute("INSERT INTO fines(loan_id, amount) VALUES (?, 0)", (loan_id,))
        cursor.execute("COMMIT")
        messagebox.showinfo("成功", f"copy_id {copy_id} 借出成功！")
    except Exception as e:
        cursor.execute("ROLLBACK")
        messagebox.showerror("發生錯誤", str(e))

def return_book():
    copy_id = entry_return.get().strip()
    cursor = conn.cursor()
    try:
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute("""
            SELECT loan_id, due_date
            FROM loans
            WHERE copy_id = ? AND return_date IS NULL
        """, (copy_id,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("ROLLBACK")
            messagebox.showerror("錯誤", f"copy_id {copy_id} 沒有可歸還紀錄")
            return

        loan_id, due_date = row
        today = datetime.now().date()

        if isinstance(due_date, str):
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        else:
            due_date = due_date.date()

        overdue_days = max((today - due_date).days, 0)
        fine = overdue_days * 5

        cursor.execute("UPDATE loans SET return_date = GETDATE() WHERE loan_id = ?", (loan_id,))
        cursor.execute("UPDATE copies SET status = 'IN' WHERE copy_id = ?", (copy_id,))
        cursor.execute("UPDATE fines SET amount = ? WHERE loan_id = ?", (fine, loan_id))

        cursor.execute("COMMIT")
        if fine > 0:
            messagebox.showinfo("成功", f"還書成功，逾期 {overdue_days} 天，罰款 {fine} 元")
        else:
            messagebox.showinfo("成功", "還書成功，無逾期")
    except Exception as e:
        cursor.execute("ROLLBACK")
        messagebox.showerror("發生錯誤", str(e))

root = tk.Tk()
root.title("館員借還書系統（修正版）")

staff_frame = tk.Frame(root)
tk.Label(staff_frame, text="館員卡號：").grid(row=0, column=0, padx=5, pady=10)
entry_staff = tk.Entry(staff_frame)
entry_staff.grid(row=0, column=1, padx=5, pady=10)
btn_login = tk.Button(staff_frame, text="登入", command=staff_login)
btn_login.grid(row=1, column=0, columnspan=2, pady=10)
staff_frame.pack()

action_frame = tk.Frame(root)

tk.Label(action_frame, text="借書功能", font=("Arial", 10, "bold")).grid(row=0, column=0, columnspan=2, pady=5)
tk.Label(action_frame, text="copy_id：").grid(row=1, column=0, sticky="e")
entry_copy = tk.Entry(action_frame)
entry_copy.grid(row=1, column=1, padx=5)
tk.Label(action_frame, text="會員卡號：").grid(row=2, column=0, sticky="e")
entry_member = tk.Entry(action_frame)
entry_member.grid(row=2, column=1, padx=5)
btn_borrow = tk.Button(action_frame, text="確認借出", command=borrow_book)
btn_borrow.grid(row=3, column=0, columnspan=2, pady=10)

tk.Label(action_frame, text="還書功能", font=("Arial", 10, "bold")).grid(row=4, column=0, columnspan=2, pady=5)
tk.Label(action_frame, text="copy_id：").grid(row=5, column=0, sticky="e")
entry_return = tk.Entry(action_frame)
entry_return.grid(row=5, column=1, padx=5)
btn_return = tk.Button(action_frame, text="確認還書", command=return_book)
btn_return.grid(row=6, column=0, columnspan=2, pady=10)

root.mainloop()
