import streamlit as st
import pandas as pd
import plotly.express as px
from utils.llm_client import LLMClient
from modules.ticket_auditing import TicketAuditor
from modules.performance_monitor import PerformanceMonitor
from modules.payroll_engine import PayrollEngine
import os

# --- 页面配置 ---
st.set_page_config(page_title="跨境电商 AI Copilot", page_icon="🛒", layout="wide")

# --- 自定义 CSS (Premium Look) ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .report-card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 初始化组件 ---
def get_clients():
    # 现在直接从 llm_client.py 读取硬编码的 Key
    return LLMClient()

client = get_clients()
db_path = 'ecommerce_data.db'

# --- 侧边栏导航 ---
st.sidebar.title("🚀 导航菜单")
page = st.sidebar.radio("请选择功能模块", ["🏠 首页概览", "🤖 智能客诉审核", "📊 运营绩效监控", "💰 薪酬核算自动化"])

# --- 模块一：首页 ---
if page == "🏠 首页概览":
    st.title("🛒 跨境电商 AI Copilot")
    st.markdown("""
    ### 欢迎使用跨境电商 AI 助手！
    本项目专为提升跨境电商运营效率而设计，深度集成了 LLM 与自动化办公能力。
    
    #### 核心优势：
    - **效率提升**：自动化处理繁琐的数据汇总与客诉审核。
    - **智能分析**：不仅仅是数据，AI 还能提供决策建议。
    - **精准核算**：规避人工核算薪酬的错误风险。
    """)
    st.image("https://images.unsplash.com/photo-1460925895917-afdab827c52f?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80", caption="Data Driven E-commerce")

# --- 模块二：客诉审核 ---
elif page == "🤖 智能客诉审核":
    st.header("🤖 智能客诉审核工具")
    st.info("批量导入客诉文件，AI 将自动进行情感分析、定责并给出处理建议。")
    
    uploaded_file = st.file_uploader("上传客诉 CSV 文件", type=["csv"])
    if not uploaded_file:
        if st.button("使用示例文件演示"):
            uploaded_file = 'sample_complaints.csv'

    if uploaded_file:
        if st.button("开始 AI 智能审核"):
            with st.spinner("AI 正在深度分析中..."):
                auditor = TicketAuditor(client)
                results_df = auditor.audit_tickets(uploaded_file)
                
                st.subheader("审核结果预览")
                st.dataframe(results_df, use_container_width=True)
                
                # 统计图表
                col1, col2 = st.columns(2)
                with col1:
                    fig_cat = px.pie(results_df, names='category', title="问题类别分布", hole=.3)
                    st.plotly_chart(fig_cat)
                with col2:
                    fig_sent = px.bar(results_df, x='sentiment', color='sentiment', title="情感倾向分析")
                    st.plotly_chart(fig_sent)

# --- 模块三：绩效监控 ---
elif page == "📊 运营绩效监控":
    st.header("📊 运营绩效 AI 监控")
    
    col_date1, col_date2 = st.columns(2)
    start_date = col_date1.date_input("开始日期", value=pd.to_datetime('2026-05-01'))
    end_date = col_date2.date_input("结束日期", value=pd.to_datetime('2026-05-10'))
    
    if st.button("查询运营数据"):
        monitor = PerformanceMonitor(db_path, client)
        df = monitor.get_performance_summary(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        
        if not df.empty:
            st.subheader("销售趋势图")
            fig_sales = px.line(df, x='date', y='sales_amount', color='sku', markers=True)
            st.plotly_chart(fig_sales, use_container_width=True)
            
            anomalies = monitor.detect_anomalies(df)
            
            st.subheader("🚨 异动预警")
            if not anomalies.empty:
                st.warning(f"检测到 {len(anomalies)} 条异动数据！")
                st.table(anomalies[['date', 'sku', 'conv_rate']])
            else:
                st.success("暂未发现显著数据异动。")
                
            with st.expander("📝 AI 运营摘要及建议", expanded=True):
                with st.spinner("AI 正在生成报告..."):
                    report = monitor.generate_ai_report(df, anomalies)
                    st.markdown(report)
        else:
            st.error("该日期范围内无数据。")

# --- 模块四：薪酬核算 ---
elif page == "💰 薪酬核算自动化":
    st.header("💰 薪酬核算自动化系统")
    
    month = st.selectbox("选择核算月份", ["2026-05", "2026-06"])
    profit_file = st.file_uploader("上传月度利润表 (Excel)", type=["xlsx"])
    
    if not profit_file:
        if st.button("使用示例利润表演示"):
            profit_file = 'monthly_profit.xlsx'

    if profit_file:
        if st.button("一键核算月度薪酬"):
            engine = PayrollEngine(db_path)
            result_df = engine.calculate_monthly_payroll(profit_file, month)
            
            st.subheader(f"{month} 薪酬结算明细")
            st.dataframe(result_df[['emp_id', 'name', 'base_salary', 'total_profit', 'commission', 'refund_amount', 'final_salary']], use_container_width=True)
            
            # 下载按钮
            csv = result_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 导出为 Excel/CSV",
                data=csv,
                file_name=f"Payroll_Summary_{month}.csv",
                mime='text/csv',
            )
            
            # 简单展示
            fig_payroll = px.bar(result_df, x='name', y='final_salary', title="员工总薪资对比", color='final_salary')
            st.plotly_chart(fig_payroll)
