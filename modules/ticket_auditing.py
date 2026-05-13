import pandas as pd
import json
from utils.llm_client import LLMClient

class TicketAuditor:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def audit_tickets(self, csv_file_path):
        df = pd.read_csv(csv_file_path)
        results = []

        system_prompt = """
        You are an expert in e-commerce customer service. 
        Analyze the customer complaint and return a JSON object with:
        - category: (Quality Issue, Logistics Issue, Refund Request, Other)
        - sentiment: (Positive, Neutral, Negative)
        - suggestion: (Approve Refund, Request Return, Reject, Escalation)
        - reason: A brief explanation.
        """

        for index, row in df.iterrows():
            complaint_text = row['Complaint_Text']
            prompt = f"Complaint content: {complaint_text}"
            
            # 调用 LLM
            response_text = self.llm_client.ask(prompt, system_prompt)
            
            # 解析 JSON (处理可能的格式问题)
            try:
                # 尝试提取 JSON 部分
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0].strip()
                elif "{" in response_text:
                    response_text = response_text[response_text.find("{"):response_text.rfind("}")+1]
                
                analysis = json.loads(response_text)
            except:
                analysis = {
                    "category": "Error",
                    "sentiment": "Error",
                    "suggestion": "Manual Review",
                    "reason": f"Failed to parse LLM response: {response_text[:50]}..."
                }
            
            results.append({**row.to_dict(), **analysis})
        
        return pd.DataFrame(results)

if __name__ == "__main__":
    # 快速测试
    client = LLMClient() # 使用 Mock 模式
    auditor = TicketAuditor(client)
    processed_df = auditor.audit_tickets('sample_complaints.csv')
    print(processed_df[['Ticket_ID', 'category', 'suggestion']])
