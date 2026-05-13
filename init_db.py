import sqlite3
import pandas as pd
import numpy as np
import os

# 数据库文件路径
DB_PATH = 'ecommerce_data.db'

def init_db():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 创建运营数据表 (Performance Monitoring)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS performance_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        sku TEXT,
        category TEXT,
        sales_amount REAL,
        clicks INTEGER,
        conversions INTEGER,
        acos REAL,
        roi REAL
    )
    ''')

    # 模拟数据生成
    np.random.seed(42)
    dates = pd.date_range(start='2026-05-01', periods=10, freq='D')
    skus = ['SKU-001', 'SKU-002', 'SKU-003', 'SKU-004', 'SKU-005']
    categories = ['Electronics', 'Home', 'Fashion', 'Toys', 'Garden']
    
    perf_records = []
    for date in dates:
        for i, sku in enumerate(skus):
            sales = np.random.uniform(500, 5000)
            clicks = np.random.randint(100, 1000)
            conversions = np.random.randint(5, 50)
            # 故意制造一个异动：SKU-001 在 5月10日 转化率暴跌
            if sku == 'SKU-001' and date.day == 10:
                conversions = 2 
            
            acos = np.random.uniform(0.1, 0.4)
            roi = np.random.uniform(2.0, 5.0)
            perf_records.append((date.strftime('%Y-%m-%d'), sku, categories[i], sales, clicks, conversions, acos, roi))
    
    cursor.executemany('INSERT INTO performance_data (date, sku, category, sales_amount, clicks, conversions, acos, roi) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', perf_records)

    # 2. 创建员工底薪表 (Payroll Automation)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS employee_base_pay (
        emp_id TEXT PRIMARY KEY,
        name TEXT,
        base_salary REAL,
        department TEXT
    )
    ''')
    employees = [
        ('E001', 'Alice', 5000, 'Operations'),
        ('E002', 'Bob', 4500, 'Operations'),
        ('E003', 'Charlie', 4800, 'Sales')
    ]
    cursor.executemany('INSERT INTO employee_base_pay VALUES (?, ?, ?, ?)', employees)

    # 3. 创建退款扣除表 (Payroll Automation)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS refund_deductions (
        emp_id TEXT,
        refund_amount REAL,
        reason TEXT,
        month TEXT
    )
    ''')
    refunds = [
        ('E001', 200, 'Logistics Damage', '2026-05'),
        ('E002', 50, 'Quality Issue', '2026-05')
    ]
    cursor.executemany('INSERT INTO refund_deductions VALUES (?, ?, ?, ?)', refunds)

    conn.commit()
    conn.close()
    print(f"Database {DB_PATH} initialized successfully.")

def generate_sample_files():
    # 生成客诉模拟 CSV
    complaints = pd.DataFrame({
        'Ticket_ID': ['T1001', 'T1002', 'T1003', 'T1004'],
        'Customer_Email': ['user1@example.com', 'user2@example.com', 'user3@example.com', 'user4@example.com'],
        'Complaint_Text': [
            "The product arrived with a broken screen. I am very disappointed.",
            "I haven't received my package yet, it's been two weeks!",
            "The size is too small, I want to return it for a refund.",
            "Great product, but the shipping was a bit slow."
        ],
        'Order_Date': ['2026-05-01', '2026-05-02', '2026-05-03', '2026-05-04']
    })
    complaints.to_csv('sample_complaints.csv', index=False)
    print("Sample complaints.csv generated.")

    # 生成利润表模拟 Excel (用于薪资计算)
    profit_data = pd.DataFrame({
        'emp_id': ['E001', 'E002', 'E003'],
        'total_profit': [20000, 15000, 30000],
        'target_achieved': [0.95, 0.80, 1.10]
    })
    profit_data.to_excel('monthly_profit.xlsx', index=False)
    print("Sample monthly_profit.xlsx generated.")

if __name__ == '__main__':
    init_db()
    generate_sample_files()
