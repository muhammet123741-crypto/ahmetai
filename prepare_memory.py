import time
from agent.memory import VectorMemory

def prepare():
    print("🦅 Ahmet Hafızayı Tazeliyor, Kimse Karışmasın...")
    memory = VectorMemory()
    # Raporları yükle (Arayüz yok, kasma derdi yok)
    memory.load_scout_reports()
    print("✅ Hafıza Mühürlendi! Artık Ahmet'i normal başlatabilirsin Dayı.")

if __name__ == "__main__":
    prepare()