import feedparser # terminale 'pip install feedparser' yazman lazım
import time
import os

class Scout:
    def __init__(self):
        # Takip edilecek kaynaklar (Burayı istediğin gibi artırabiliriz)
        self.sources = [
            "https://www.webrazzi.com/feed/", 
            "https://search.cnnturk.com/rss/turkiye",
            "https://feeds.feedburner.com/teknolojioku"
        ]
        self.report_file = "data/scout_reports.txt"
        
        if not os.path.exists("data"):
            os.makedirs("data")

    def look_around(self):
        print("🕵️ Ahmet Gece Nöbetine Çıktı...")
        new_intel = ""
        
        for url in self.sources:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:5]: # Her kaynaktan son 5 haber
                    report = f"BAŞLIK: {entry.title}\nÖZET: {entry.summary[:200]}...\nKAYNAK: {entry.link}\n---\n"
                    new_intel += report
            except Exception as e:
                print(f"⚠️ Kaynak taranırken sıkıntı çıktı dayı: {e}")

        if new_intel:
            with open(self.report_file, "a", encoding="utf-8") as f:
                f.write(f"\n--- NÖBET RAPORU ({time.ctime()}) ---\n")
                f.write(new_intel)
            print("✅ Ahmet istihbaratı topladı, heybesine attı.")

    def start_night_shift(self, interval=3600):
        """Sen kapatana kadar saatte bir tur atar."""
        while True:
            self.look_around()
            print(f"💤 Ahmet biraz kestiriyor, {interval/60} dakika sonra tekrar devriyeye çıkacak...")
            time.sleep(interval)

if __name__ == "__main__":
    saha_ajani = Scout()
    saha_ajani.start_night_shift()