import ollama
import json
import re
import time
from agent.memory import MemoryManager
from agent.tools import ToolRegistry

class Agent:
    def __init__(self):
        self.model_name = "ahmet" # Yerel model (Llama 3, Mistral vb.)
        self.memory = MemoryManager()
        self.tools = ToolRegistry()
        self.max_loops = 5 # Derinlemesine araştırma için 5 tur limit.

    def clean_json(self, text):
        """Modelin JSON dışındaki tüm gürültüsünü cerrahi hassasiyetle temizler."""
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if not match: return None
            # JSON'u bozan gizli karakterleri ve satır sonlarını normalize et
            json_str = match.group().replace('\n', ' ').replace('\r', '').strip()
            return json_str
        except Exception: return None

    def run(self, user_input):
        print(f"\n{'='*60}\n📡 [SİSTEM]: Otonom İstihbarat ve Muhakeme Motoru Aktif...")
        print(f"📥 [TALİMAT]: {user_input}")
        
        # Hafıza Katmanı (Sadece son 2 etkileşim - Konu karışıklığını önlemek için)
        history = self.memory.load_memory().get("history", [])[-2:]
        
        # SİSTEM ANAYASASI: Ahmet'in 'Ezberci' değil 'Araştırmacı' olmasını sağlar.
        system_rules = """
        SEN AHMET'SİN. Bir 'Sürekli Kanıt Arayan' (Evidence-Based) baş araştırmacısısın.
        Sadece JSON formatında cevap ver.

        [OPERASYONEL KURALLAR]:
        1. SIFIR GÜVEN: Hafızandaki (Memory) hiçbir bilgiye (skor, fiyat, tarih) doğrudan güvenme.
        2. İLK ADIM (ARAMA): Bilgi odaklı sorularda ilk aksiyonun MUTLAKA 'search_and_browse' olmalı.
        3. KANIT ANALİZİ: 'Observation' içindeki rakamları, tarihleri ve isimleri cımbızla çek. 
        4. ÇELİŞKİ GİDERME: Eğer internet verisi (Observation) senin hafızanla çelişiyorsa, hafızanı ÇÖPE AT ve yeni veriyi mühürle.
        5. KARAR: Bilgi kesin, güncel (2026) ve netse 'final_answer' ver. Eğer veri çelişkiliyse aramayı derinleştir.

        [JSON ŞABLONU]:
        {
            "thought": "Neden internete gidiyorum? Hangi kanıtları toplayacağım?",
            "action": "search_and_browse" veya "final_answer",
            "parameters": {"query": "arama terimi"} veya {"message": "kanıtlanmış net cevap"}
        }
        """

        current_obs = ""
        # Kullanıcının "yanlış", "karıştırdın" gibi itirazlarını 'Şüphe Sinyali' olarak işle
        if any(x in user_input.lower() for x in ["yanlış", "karıştırdın", "hatalı", "değil", "doğru değil"]):
            current_obs = "\n[🚨 ŞÜPHE SİNYALİ]: Kullanıcı önceki bilginin yanlış olduğunu belirtti. Hafızayı reddet ve sıfırdan kanıt topla!"

        for i in range(self.max_loops):
            print(f"🔄 [ADIM {i+1}]: Ahmet muhakeme yapıyor...")
            
            # Dinamik Prompt: Ahmet'e her adımda güncel durumu ve kanıtları gösteriyoruz.
            full_context = f"{system_rules}\n\nGEÇMİŞ: {history}\nKULLANICI: {user_input}\n{current_obs}"
            
            # 2. turdan sonra veri geldiyse Ahmet'i senteze zorla
            if i >= 1 and len(current_obs) > 100:
                full_context += "\n[KRİTİK]: Elinde internet verisi var! Artık arama yapmayı bırak ve bu veriyi kullanarak 'final_answer' ver."

            try:
                response = ollama.chat(model=self.model_name, messages=[{'role': 'user', 'content': full_context}])
                raw_content = response.get('message', {}).get('content', "").strip()
                
                json_str = self.clean_json(raw_content)
                if not json_str:
                    current_obs += "\nObservation: Lütfen sadece JSON formatında cevap ver!"
                    continue
                
                data = json.loads(json_str)
                action = data.get("action")
                params = data.get("parameters", {})
                thought = data.get("thought", "Analiz ediliyor...")

                print(f"🧠 [DÜŞÜNCE]: {thought}")

                if action == "final_answer":
                    # Bilgi sorusunda internete gitmeden bitirmeye kalkarsa durdur
                    if i == 0 and any(x in user_input.lower() for x in ["kaç", "ne", "kim", "skor", "fiyat"]):
                        current_obs += "\nObservation: Henüz internetten kanıt toplamadın. Lütfen önce 'search_and_browse' yap."
                        continue
                    
                    answer = params.get("message")
                    if answer and len(answer) > 5:
                        self.memory.save_interaction(user_input, answer)
                        print(f"✅ [OPERASYON TAMAMLANDI]\n{'='*60}")
                        return answer
                
                elif action == "search_and_browse":
                    query = params.get("query")
                    if not query: continue
                    
                    obs_data = self.tools.search_and_browse(query)
                    # Gözlemi modele geri bas (Max 2500 karakter)
                    current_obs = f"\nObservation: {obs_data[:2500]}\n\n[ANALİZ]: Bu verideki bilgileri eski bilgilerle kıyasla ve cevabı güncelle."
                    print(f"👁️ [GÖZLEM]: Sahadan gerçek veri çekildi.")

            except Exception as e:
                print(f"❌ Kritik Hata: {e}")
                continue

        return "Dayı araştırdım ama internetteki veriler arasında net bir karara varamadım."