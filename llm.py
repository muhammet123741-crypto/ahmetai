import requests
import json

class GeminiLLM:
    def __init__(self):
        # API Anahtarını buraya yapıştır
        self.api_key = "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"
        self.url = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, prompt: str):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:3000", 
            "X-Title": "Mami Agent Local"
        }
        
        data = {
            # MODEL İSMİNİ ŞU ŞEKİLDE GÜNCELLEDİK (EN GARANTİ ÜCRETSİZ GEMİNİ):
            "model": "google/gemini-2.0-flash-001", 
            "messages": [
                {"role": "system", "content": "Sen sadece JSON ile cevap veren profesyonel bir ajansın."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.1
        }

        try:
            response = requests.post(self.url, headers=headers, data=json.dumps(data), timeout=60)
            
            if response.status_code != 200:
                # Hata kodunu ve mesajını loglara basar
                return f"Gemini API Hatası ({response.status_code}): {response.text}"
                
            result = response.json()
            # Cevabı içinden çekip alıyoruz
            return result['choices'][0]['message']['content']
        except Exception as e:
            return f"Bağlantı Hatası: {str(e)}"