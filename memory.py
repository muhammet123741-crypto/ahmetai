import json
import os
import time
import chromadb
import datetime

# --- 1. KISIM: ARAYÜZ (UI) İÇİN KISA SÜRELİ SOHBET GEÇMİŞİ ---
class MemoryManager:
    def __init__(self, file_path="agent/memory.json"):
        self.file_path = file_path
        if not os.path.exists("agent"): os.makedirs("agent")
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump({"sessions": {}}, f)

    def load_memory(self):
        """Eski formatı otomatik yeniye çeviren akıllı yükleyici."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # EĞER ESKİ FORMATSA (sessions anahtarı yoksa) YENİSİNİ OLUŞTUR
                if "sessions" not in data:
                    return {"sessions": {}}
                return data
        except: 
            return {"sessions": {}}

    def save_interaction(self, session_id, user_text, agent_text):
        """Seans bazlı kayıt yapar."""
        data = self.load_memory()
        
        # Seans yoksa oluştur
        if session_id not in data["sessions"]:
            data["sessions"][session_id] = {
                "title": user_text[:25] + "...",
                "date": time.strftime("%d %B %H:%M"),
                "messages": []
            }
        
        # Mesajı ekle
        data["sessions"][session_id]["messages"].append({
            "user": user_text,
            "agent": agent_text,
            "time": time.strftime("%H:%M")
        })
        
        # Dosyayı kaydet
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


# --- 2. KISIM: AHMET'İN KARAKTERİ İÇİN UZUN SÜRELİ VEKTÖR HAFIZASI ---
class VectorMemory:
    def __init__(self):
        # Hafızanın bilgisayarda kalıcı olarak duracağı gizli klasör
        self.db_path = os.path.join(os.getcwd(), "agent_memory_db")
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Ahmet'in anı koleksiyonu (Yoksa oluşturur, varsa bağlanır)
        self.collection = self.client.get_or_create_collection(name="ahmet_long_term")

    def save_memory(self, text):
        """Yeni bir bilgiyi vektöre (matematiğe) çevirip beynine kazır."""
        blacklist = ["yok", "boş", "bilgi yok", "null", "none"]
        if not text or any(x in text.lower() for x in blacklist):
            return

        # Benzersiz bir anı kimliği (ID) oluştur
        doc_id = f"mem_{datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        
        # ChromaDB bu metni otomatik olarak alır, vektöre çevirir ve saklar
        self.collection.add(
            documents=[text],
            metadatas=[{"date": str(datetime.datetime.now())}],
            ids=[doc_id]
        )
        print("🧠 [VEKTÖR HAFIZA]: Yeni bilgi kalıcı arşive mühürlendi.")

    def recall_memory(self, query, n_results=3):
        """Sadece konuşulan GÜNCEL KONUYLA ALAKALI geçmiş anıları cımbızlar."""
        try:
            # Eğer arşiv boşsa boşuna arama yapmasın
            if self.collection.count() == 0:
                return "Geçmişe dair henüz bir not yok."
                
            # Sorduğumuz soruya en çok benzeyen anıları getirir
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count())
            )
            
            if results and results['documents'] and len(results['documents'][0]) > 0:
                fetched_memories = results['documents'][0]
                return "\n".join([f"- {mem}" for mem in fetched_memories])
                
            return "Bu konuyla alakalı geçmiş bir bilgi bulunamadı."
            
        except Exception as e:
            return f"Hafıza çekilirken temassızlık oldu: {str(e)}"