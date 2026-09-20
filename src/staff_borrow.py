
import tkinter as tk
from tkinter import messagebox
from db import connect

conn = connect()

def staff_login():
    staff_card = entry_staff.get().strip()
    cursor = conn.cursor()
    cursor.execute("SELECT mid FROM members WHERE card_no = ? AND role = 'staff'", (staff_card,))
    row = cursor.fetchone()
    if not row:
        messagebox.showerror("登入失敗", "無此館員卡號或權限不足")
    else:
        messagebox.showinfo("登入成功", "歡迎進入借書管理系統")
        staff_frame.pack_forget()
        borrow_frame.pack()

def borrow_book():
    copy_id = entry_copy.get().strip()
    member_card = entry_member.get().strip()
    cursor = conn.cursor()
    try:
        print("[DEBUG] 開始交易")
        cursor.execute("BEGIN TRANSACTION")

        print(f"[DEBUG] 嘗試借出 copy_id={copy_id}")
        cursor.execute("UPDATE copies SET status = 'OUT' WHERE copy_id = ? AND status = 'IN'", (copy_id,))
        print(f"[DEBUG] 更新 copies 狀態 rowcount = {cursor.rowcount}")
        if cursor.rowcount == 0:
            cursor.execute("ROLLBACK")
            messagebox.showerror("錯誤", f"copy_id {copy_id} 無法借出（可能已借出）")
            return

        print(f"[DEBUG] 查詢會員卡號：{member_card}")
        cursor.execute("SELECT mid FROM members WHERE card_no = ?", (member_card,))
        row = cursor.fetchone()
        if not row:
            cursor.execute("ROLLBACK")
            messagebox.showerror("錯誤", "找不到此會員")
            return
        mid = row[0]
        print(f"[DEBUG] 對應會員 ID = {mid}")

        print("[DEBUG] 插入 loans 並抓回 loan_id")
        cursor.execute("""
            INSERT INTO loans(copy_id, borrower_id, loan_date, due_date)
            OUTPUT INSERTED.loan_id
            VALUES (?, ?, GETDATE(), DATEADD(day, 14, GETDATE()))
        """, (copy_id, mid))
        loan_row = cursor.fetchone()
        print("[DEBUG] loan_row =", loan_row)

        if not loan_row or not loan_row[0]:
            cursor.execute("ROLLBACK")
            messagebox.showerror("錯誤", "無法取得 loan_id，借書失敗")
            return

        loan_id = int(loan_row[0])
        print(f"[DEBUG] 成功取得 loan_id={loan_id}")

        print("[DEBUG] 插入 fines")
        cursor.execute("INSERT INTO fines(loan_id, amount) VALUES (?, 0)", (loan_id,))

        print("[DEBUG] COMMIT")
        cursor.execute("COMMIT")
        messagebox.showinfo("成功", f"已成功借出 copy_id {copy_id} 給卡號 {member_card}")

    except Exception as e:
        cursor.execute("ROLLBACK")
        messagebox.showerror("發生錯誤", str(e))

# GUI 主畫面
root = tk.Tk()
root.title("館員借書系統（OUTPUT INSERTED 版）")

staff_frame = tk.Frame(root)
tk.Label(staff_frame, text="館員卡號：").grid(row=0, column=0, pady=10)
entry_staff = tk.Entry(staff_frame)
entry_staff.grid(row=0, column=1, pady=10)
btn_login = tk.Button(staff_frame, text="登入", command=staff_login)
btn_login.grid(row=1, column=0, columnspan=2, pady=10)
staff_frame.pack()

borrow_frame = tk.Frame(root)
tk.Label(borrow_frame, text="複本 ID（copy_id）：").grid(row=0, column=0, sticky="e")
entry_copy = tk.Entry(borrow_frame)
entry_copy.grid(row=0, column=1)
tk.Label(borrow_frame, text="會員卡號：").grid(row=1, column=0, sticky="e")
entry_member = tk.Entry(borrow_frame)
entry_member.grid(row=1, column=1)
btn_borrow = tk.Button(borrow_frame, text="確認借出", command=borrow_book)
btn_borrow.grid(row=2, column=0, columnspan=2, pady=10)

root.mainloop()
