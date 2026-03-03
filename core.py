import os
import json
import re
import anthropic 
from datetime import datetime
from agent.memory import MemoryManager, VectorMemory
from agent.tools import ToolRegistry

class Agent:
    def __init__(self):
        # API Anahtarını buraya sabitliyoruz
        self.api_key = "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"
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model_name = "claude-sonnet-4-6" 
        
        self.memory = MemoryManager()
        self.vector_db = VectorMemory() 
        self.tools = ToolRegistry(api_key=self.api_key) 
        self.max_iterations = 10 # Zincirleme harekat için tur sayısını artırdık

    def run(self, user_input, session_id):
        simdi = datetime.now()
        su_an = simdi.strftime("%d %B %Y, %A %H:%M") 
        
        print(f"\n{'='*60}\n📡 [SİSTEM]: Ahmet (Claude 4.6) Göreve Başlıyor...")
        print(f"⏰ [ZAMAN]: {su_an}")
        
        # 1. HAFIZA VE GEÇMİŞ YÜKLEME (Orijinal Mantık)
        past_notes = self.vector_db.recall_memory(user_input)
        history_data = self.memory.load_memory()
        
        current_session = history_data.get("sessions", {}).get(session_id, {})
        session_history = current_session.get("messages", [])[-5:]
        
        context = ""
        
        # 2. SENİN ATTIĞIN O ORİJİNAL SİSTEM PROMPTU (BİREBİR AYNI)
        system_prompt = f"""
        ADIN: AHMET. Samsun Atakum'da yaşayan, 27 yaşında, mert, zeki ve Türkiye gündeminin nabzını tutan bir Sosyal Medya Uzmanısın.
        PATRONUN: MAMI DAYI.
        [KRİTİK]: ŞU AN GERÇEKTEN {su_an} TARİHİNDEYİZ.
        [GEÇMİŞ ANILAR (Vektör)]: {past_notes}

        [KİMLİK VE YETKİ UYARISI - ÇOK KRİTİK]:
        Sen sıradan bir sohbet botu DEĞİLSİN! Sen Playwright yetkileriyle donatılmış, bilgisayarı kontrol edebilen bir icraat adamısın.
        ASLA "Hesap bilgilerin bende yok", "Tweet atamam" gibi bahaneler üretme. X hesabında oturum zaten açık. 
        Patronun sana "Etkileşim yap" veya "Isınma turu at" dediğinde ASLA yeni tweet atmayacaksın! Görevin başkalarının tweetlerini bulup Muhabbete girmektir.

        [YETKİ VE ARAÇLAR]: 
        - `get_user_latest_tweet`: Hedef hesabın (Örn: BPT_Haber) son tweetini çekmek için.
        - `like_and_reply`: O tweeti beğenip altına samimi bir 2026 X jargonu yorumu bırakmak için.
        - `search_x_latest`: Viral avı veya trend analizi için (Örn: "lang:tr min_faves:20000").
        - `download_viral_media`: Komik tweetin URL'sini verip videoyu/resmi indirmek için.
        - `post_to_x`: Yalnızca YENİ içerik üretmen istendiğinde kullan. Isınma turunda bu araç YASAKTIR.
        
        [2026 X TÜRKİYE MİZAH KODLARI VE STRATEJİSİ]:
        1. VİRAL MEDYA AVI: X'te video/resim bulurken "filter:native_video" veya "filter:media" kullan.
        2. TREND ANALİZİ (AÇIK KİTAP SINAVI): Medyayı indirdikten sonra ÖNCE `search_x_latest` ile güncel Türk X feed'ini oku, vibe'ı analiz et.
        3. 2026 TÜRKİYE YERELLEŞTİRME: 
           - ❌ YASAK: Boomer/Caps mizahı (Maaş yattı mı, Kim Jong Un vb.) KESİNLİKLE YASAK.
           - ✅ İSTENEN: Gen-Z / Shitpost mizahı. Kısa, noktalama işareti olmayan, absürt ve ironik tespitler.

        [BÜYÜME VE ETKİLEŞİM STRATEJİSİ]:
        1. TOPLULUK YÖNETİMİ: Büyük hesaplardaki tartışmaları bul ve zekice, ironik yorumlar yap (like_and_reply).
        2. VİRAL KURGU: Yabancı feedlerden bulduğun medyaları `download_viral_media` ile indir ve yerelleştir.
        3. GÖRSEL GÜÇ: Gerektiğinde `generate_image` ile 4060 Ti'ın gücünü kullanarak surrealist içerikler üret.
        4. CEVAP DÖNGÜSÜ: Gelen her yoruma etkileşimi artırmak için samimi veya ironik bir cevap yapıştır.
        
        [ÖRNEK YERELLEŞTİRME EĞİTİMİ]:
        - Yabancı Tweet: "Me calculating how many hours of sleep I can get if I fall asleep right now"
        - ❌ KÖTÜ: Şu an uyursam kaç saat uyuyacağımı hesaplarken ben...
        - ✅ AHMET: Gece 3'te sabahki mesaiye uyanmak için kalan 3.5 saatlik uykumu hesaplarken beynimin girdiği o şekil.
        
        [ETKİLEŞİM VE ISINMA STRATEJİSİ]:
        1. ANALİZ: Tweeti oku. Kendi hayatından (Opel Astra J, fitness antrenmanları, Martı TAG maceraları) esintiler içeren ironik yorumlar yap.
        2. YORUM TARZI: Yanıtların kısa ve 2026 X jargonuna uygun olsun. Asla bot gibi "Harika paylaşım" deme.
        - Örn: "halis mi bu ya", "anlık ben", "hocam sonuna kadar haklısın", "zortladım" gibi doğal tepkiler ver.

        [KURAL]: Sadece JSON formatında cevap ver.
        - {{"thought": "..", "action": "get_user_latest_tweet", "username": "BPT_Haber"}}
        - {{"thought": "..", "action": "like_and_reply", "url": "https://x.com/..", "reply_text": "hocam bu tespit beni bitirdi halis mi bu"}}
        - {{"thought": "..", "action": "post_to_x", "tweets": [".."], "media_path": ".."}}
        - {{"thought": "..", "action": "final_answer", "answer": "..", "new_memory": ".."}}
        """

        # 3. MUHAKEME DÖNGÜSÜ
        for i in range(self.max_iterations):
            print(f"🔄 [MUHAKEME {i+1}]: Ahmet analiz ediyor...")
            try:
                message = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=2048,
                    system=system_prompt,
                    messages=[{"role": "user", "content": f"İSTEK: {user_input}\nTOPLANAN VERİ: {context}"}]
                )
                
                res_json = self._extract_json(message.content[0].text)
                if not res_json: break

                action = res_json.get("action")
                thought = res_json.get("thought", "Düşünüyorum...")
                print(f"🧠 [DÜŞÜNCE]: {thought}")

                # --- AKSİYON MERKEZİ ---
                if action == "final_answer":
                    answer = res_json.get("answer")
                    if res_json.get("new_memory"): 
                        self.vector_db.save_memory(res_json.get("new_memory"))
                    return answer

                elif action == "search_x_latest":
                    query = res_json.get("query")
                    obs = self.tools.search_x_latest(query)
                    context += f"\n- X İstihbaratı ({query}): {obs[:1500]}"

                elif action == "download_viral_media":
                    url = res_json.get("url")
                    obs = self.tools.download_viral_media(url)
                    context += f"\n- İndirilen Medya Yolu: {obs}"

                elif action == "get_user_latest_tweet":
                    user = res_json.get("username")
                    obs = self.tools.get_user_latest_tweet(user)
                    context += f"\n- @{user} Son Tweeti: {obs}"

                elif action == "post_to_x":
                    tweets = res_json.get("tweets") or [] # NoneType Zırhı
                    media_path = res_json.get("media_path")
                    print(f"🐦 [PAYLAŞIM]: Ahmet X'e sızıyor...")
                    obs = self.tools.post_to_x(tweets, media_path)
                    
                    tweet_txt = tweets[0] if isinstance(tweets, list) and len(tweets) > 0 else "İçerik"
                    context += f"\n- Kendi Paylaşımım: {tweet_txt} | Durum: {obs}"
                    if res_json.get("new_memory"): 
                        self.vector_db.save_memory(res_json.get("new_memory"))

                elif action == "like_and_reply":
                    url = res_json.get("url")
                    text = res_json.get("reply_text")
                    obs = self.tools.like_and_reply(url, text)
                    context += f"\n- Etkileşim Tamam: {url} adresine '{text}' yorumu yapıldı. | Durum: {obs}"
                    if res_json.get("new_memory"): 
                        self.vector_db.save_memory(res_json.get("new_memory"))

                elif action == "generate_image":
                    prm = res_json.get("prompt")
                    obs = self.tools.generate_image(prm)
                    context += f"\n- Üretilen Görsel Yolu: {obs}"

                elif action == "visual_recon":
                    url = res_json.get("url")
                    q = res_json.get("question")
                    obs = self.tools.visual_recon(url, q)
                    context += f"\n- Görsel Analiz Sonucu: {obs}"

                elif action == "search_and_browse":
                    q = res_json.get("query")
                    obs = self.tools.search_and_browse(q)
                    context += f"\n- Araştırma Sonucu: {obs}"

                elif action == "create_shorts_video":
                    t = res_json.get("text")
                    topic = res_json.get("topic_name")
                    obs = self.tools.create_shorts_video(t, topic)
                    context += f"\n- Video Oluşturuldu: {obs}"
                
            except Exception as e:
                print(f"❌ HATA: {e}")
                break

        return self._generate_final_fallback(user_input, context)

    def _extract_json(self, text):
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match: return json.loads(match.group())
            return None
        except: return None

    def _generate_final_fallback(self, user_input, context):
        final_prompt = f"Sen Ahmet'sim. Elimdeki verilerle Mami Dayı'ya rapor yaz. VERİ: {context}. Soru: {user_input}"
        try:
            message = self.client.messages.create(model=self.model_name, max_tokens=2048, messages=[{"role": "user", "content": final_prompt}])
            return message.content[0].text
        except: return "Sistemde bir temassızlık oldu dayı!"