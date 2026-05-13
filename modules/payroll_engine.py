import pandas as pd
import sqlite3

class PayrollEngine:
    def __init__(self, db_path):
        self.db_path = db_path

    def calculate_monthly_payroll(self, profit_excel_path, month):
        conn = sqlite3.connect(self.db_path)
        
        # 1. 加载底薪
        base_pay_df = pd.read_sql_query("SELECT * FROM employee_base_pay", conn)
        
        # 2. 加载退款扣除
        refunds_df = pd.read_sql_query(f"SELECT * FROM refund_deductions WHERE month = '{month}'", conn)
        
        # 3. 加载利润数据 (Excel)
        profit_df = pd.read_excel(profit_excel_path)
        
        conn.close()

        # 合并数据
        merged = base_pay_df.merge(profit_df, on='emp_id', how='left')
        merged = merged.merge(refunds_df[['emp_id', 'refund_amount']], on='emp_id', how='left').fillna(0)

        # 4. 阶梯式提成逻辑
        # 利润 < 10000: 2%
        # 10000 - 20000: 5%
        # > 20000: 8%
        def calculate_commission(profit):
            if profit < 10000:
                return profit * 0.02
            elif profit < 20000:
                return 10000 * 0.02 + (profit - 10000) * 0.05
            else:
                return 10000 * 0.02 + 10000 * 0.05 + (profit - 20000) * 0.08

        merged['commission'] = merged['total_profit'].apply(calculate_commission)
        
        # 最终薪资 = 底薪 + 提成 - 退款扣款
        merged['final_salary'] = merged['base_salary'] + merged['commission'] - merged['refund_amount']
        
        return merged

if __name__ == "__main__":
    engine = PayrollEngine('ecommerce_data.db')
    result = engine.calculate_monthly_payroll('monthly_profit.xlsx', '2026-05')
    print(result[['name', 'base_salary', 'commission', 'refund_amount', 'final_salary']])
