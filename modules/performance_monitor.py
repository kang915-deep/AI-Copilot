import sqlite3
import pandas as pd
from utils.llm_client import LLMClient

class PerformanceMonitor:
    def __init__(self, db_path, llm_client: LLMClient):
        self.db_path = db_path
        self.llm_client = llm_client

    def get_performance_summary(self, start_date, end_date):
        conn = sqlite3.connect(self.db_path)
        query = f"""
        SELECT date, sku, category, sales_amount, conversions, clicks,
               (CAST(conversions AS FLOAT) / NULLIF(clicks, 0)) as conv_rate
        FROM performance_data
        WHERE date BETWEEN '{start_date}' AND '{end_date}'
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def detect_anomalies(self, df):
        # 简单逻辑：转化率低于平均值 50% 的 SKU
        avg_conv_rate = df['conv_rate'].mean()
        anomalies = df[df['conv_rate'] < avg_conv_rate * 0.5]
        return anomalies

    def generate_ai_report(self, df, anomalies):
        summary_stats = df.groupby('category')['sales_amount'].sum().to_dict()
        anomaly_list = anomalies[['date', 'sku', 'conv_rate']].to_dict(orient='records')

        prompt = f"""
        Based on the following e-commerce data, generate a daily performance summary and risk warning:
        - Total Sales by Category: {summary_stats}
        - Detected Anomalies: {anomaly_list}
        
        Please provide:
        1. Overall trend analysis.
        2. Specific reasons for why these SKUs might be underperforming.
        3. Actionable advice for the operations team.
        """
        
        report = self.llm_client.ask(prompt, "You are a senior e-commerce operations manager.")
        return report

if __name__ == "__main__":
    client = LLMClient()
    monitor = PerformanceMonitor('ecommerce_data.db', client)
    data = monitor.get_performance_summary('2026-05-01', '2026-05-10')
    anomalies = monitor.detect_anomalies(data)
    report = monitor.generate_ai_report(data, anomalies)
    print("AI Report Summary:\n", report)
