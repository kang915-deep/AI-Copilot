import openai
import os

class LLMClient:
    def __init__(self, api_key="sk-YOUR_DEEPSEEK_API_KEY", base_url="https://api.deepseek.com", model="deepseek-chat"):
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url
        self.model = model
        
        if self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
        else:
            self.client = None

    def ask(self, prompt, system_prompt="You are a helpful assistant."):
        if not self.client:
            return self._mock_response(prompt)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling LLM: {str(e)}"

    def _mock_response(self, prompt):
        """当没有 API Key 时返回模拟响应"""
        prompt_lower = prompt.lower()
        if "complaint" in prompt_lower or "ticket" in prompt_lower:
            return "{\"category\": \"Quality Issue\", \"sentiment\": \"Negative\", \"suggestion\": \"Full refund\", \"reason\": \"The customer reported a broken item which is a clear quality violation.\"}"
        elif "performance" in prompt_lower or "data" in prompt_lower:
            return "Based on the data provided, SKU-001 shows a significant drop in conversion rate (from 5% to 0.5%). This may be due to stock issues or negative reviews. Recommend checking the product page immediately."
        return "This is a mock response from the AI assistant. Please provide an API key for real analysis."
