import time
import schedule
from datetime import datetime
from agent.core import Agent
import uuid

# Ahmet'in beyin ünitesi
ahmet = Agent()

# Radara takılacak kritik başlıklar (Burayı dilediğin gibi genişlet kanki)
RADAR_LISTESI = ["#sondakika", "Bitcoin crash", "recession news", "Elon Musk X"]

def radar_operasyonu():
    print(f"\n📡 [EKONOMİK RADAR]: {datetime.now().strftime('%H:%M')} - Nöbet başlıyor...")
    
    # Her 3 saatte bir uyandığında tüm listeyi tek bir muhakemede taratabiliriz
    # Böylece her konu için ayrı API çağrısı yapıp bakiye bitirmeyiz.
    session_id = str(uuid.uuid4())[:8]
    
    # Toplu istihbarat komutu (Tek çağrı, çok verim)
    toplu_sorgu = " , ".join(RADAR_LISTESI)
    
    print(f"🔍 X üzerinde taze bilgiler toplanıyor: {toplu_sorgu}")
    
    try:
        # Önce X'ten verileri çekiyoruz (Bu kısım bedava, Playwright yapıyor)
        taze_veri = ahmet.tools.search_x_latest(toplu_sorgu)
        
        # Ahmet'e tek seferde analiz ettiriyoruz (Tasarruf noktası burası!)
        komut = f"""
        Şu taze X verilerini incele: {taze_veri}
        1. Eğer kriptoda ani bir çöküş veya çok büyük bir haber varsa HEMEN flood patlat.
        2. Eğer piyasa normalse sadece kısa bir özet geç ve 'Sakin' de.
        Maliyetten kaçınmak için sadece ÇOK KRİTİK durumlarda tweet at.
        """
        
        rapor = ahmet.run(komut, session_id)
        
        if "Sakin" not in rapor:
            print("🔥 KRİTİK: Ahmet önemli bir şey yakaladı ve mermiyi sıktı!")
            ahmet.memory.save_interaction(session_id, "Radar Operasyonu", rapor)
        else:
            print("🟢 Radar temiz, piyasa sakin. Bakiye korundu.")
            
    except Exception as e:
        print(f"⚠️ Nöbet sırasında pürüz çıktı: {e}")

# --- 3 SAATLİK PERİYOT ---
schedule.every(3).hours.do(radar_operasyonu)

print("🦅 [SİSTEM]: Ahmet 'Ekonomik Radar' aktif! 3 saatte bir devriyeye çıkacak.")
print("💰 Bakiye dostu mod devrede. İlk tarama için bekleniyor...")

while True:
    schedule.run_pending()
    time.sleep(60)