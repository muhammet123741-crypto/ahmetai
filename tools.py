import time
import os
import base64
import anthropic
import requests
import edge_tts
import asyncio
import yt_dlp
from playwright.sync_api import sync_playwright
from moviepy import AudioFileClip, ImageClip

class ToolRegistry:
    def __init__(self, api_key=None):
        self.user_data_dir = os.path.join(os.getcwd(), "x_profil")
        if not os.path.exists(self.user_data_dir):
            os.makedirs(self.user_data_dir)
        self.api_key = api_key 

    # --- 1. MEDYA İNDİRİCİ ---
    def download_viral_media(self, url):
        """X'ten duruma göre VİDEO veya FOTOĞRAF indirir."""
        print(f"📥 [MEDYA AVCISI]: {url} inceleniyor...")
        try:
            ydl_opts = {
                'outtmpl': os.path.join(os.getcwd(), 'viral_medya.%(ext)s'),
                'format': 'best', 'quiet': True, 'noplaylist': True
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                return os.path.join(os.getcwd(), f"viral_medya.{info.get('ext', 'mp4')}")
        except Exception:
            print(f"⚠️ Video yok, fotoğrafa geçiliyor...")
            with sync_playwright() as p:
                try:
                    context = p.chromium.launch_persistent_context(user_data_dir=self.user_data_dir, headless=False, args=["--disable-blink-features=AutomationControlled"])
                    page = context.new_page()
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(5)
                    img_locator = page.locator('img[src*="pbs.twimg.com/media"]')
                    if img_locator.count() > 0:
                        img_url = img_locator.first.get_attribute("src")
                        if "name=" in img_url: img_url = img_url.split("name=")[0] + "name=large"
                        response = requests.get(img_url)
                        file_path = os.path.join(os.getcwd(), 'viral_medya.jpg')
                        with open(file_path, 'wb') as f: f.write(response.content)
                        context.close(); return file_path
                    else: context.close(); return "Hata: Resim yok."
                except Exception as e: return f"Hata: {str(e)}"

    # --- 2. VİZYON RECON ---
    def visual_recon(self, url, question):
        """Siteye gidip Vision ile analiz yapmasını sağlar."""
        if not self.api_key: return "Dayı Vision API anahtarı eksik!"
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--start-maximized"])
                context = browser.new_context(no_viewport=True)
                page = context.new_page()
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                time.sleep(5)
                screenshot_bytes = page.screenshot()
                browser.close()
                base64_image = base64.b64encode(screenshot_bytes).decode('utf-8')
                client = anthropic.Anthropic(api_key=self.api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-6", max_tokens=1024,
                    messages=[{"role": "user", "content": [{"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": base64_image}}, {"type": "text", "text": question}]}]
                )
                return response.content[0].text
            except Exception as e: return f"Hata: {str(e)}"

    # --- 3. GİZLİ ARAŞTIRMA ---
    def search_and_browse(self, query):
        """Hayalet modunda DuckDuckGo Lite üzerinden veri çeker."""
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled", "--start-maximized"])
                page = browser.new_page()
                page.goto("https://lite.duckduckgo.com/lite/", wait_until="domcontentloaded")
                page.fill("input[name='q']", query)
                page.keyboard.press("Enter"); time.sleep(4)
                results = page.locator(".result-snippet").all_text_contents()
                browser.close(); return "\n".join(results[:5]) if results else "Veri yok."
            except Exception as e: return f"Hata: {str(e)}"

    # --- 4. X RADARI ---
    def search_x_latest(self, query):
        """X'in canlı akışını ve LİNKLERİNİ okur."""
        print(f"🐦 [X RADARI]: '{query}' aranıyor...")
        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(self.user_data_dir, headless=False, args=["--disable-blink-features=AutomationControlled"])
                page = context.new_page()
                page.goto(f"https://x.com/search?q={query}&f=live")
                time.sleep(10) 
                articles = page.locator('article[data-testid="tweet"]').all()
                res = []
                for art in articles[:6]:
                    text = art.inner_text().replace('\n', ' | ')
                    links = art.locator('a[href*="/status/"]').all()
                    url = f"https://x.com{links[0].get_attribute('href')}" if links else "Yok"
                    res.append(f"Metin: {text}\nURL: {url}")
                context.close(); return "\n---\n".join(res)
            except Exception as e: return str(e)

    # --- 5. POST TO X ---
    def post_to_x(self, tweets, media_path=None):
        """Flood oluşturur - İnsansı ve Yavaşlatılmış Tempo."""
        print(f"🐦 [OPERASYON]: Flood başlatılıyor (İnsansı Tempo)...")
        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(self.user_data_dir, headless=False, args=["--disable-blink-features=AutomationControlled"])
                page = context.new_page()
                page.goto("https://x.com/compose/post", wait_until="domcontentloaded")
                time.sleep(10) 
                if isinstance(tweets, str): tweets = [tweets]
                if media_path and os.path.exists(media_path):
                    page.locator('input[data-testid="fileInput"]').first.set_input_files(media_path)
                    time.sleep(10)
                for i, text in enumerate(tweets):
                    selector = f'div[data-testid="tweetTextarea_{i}"]'
                    page.wait_for_selector(selector, state="visible")
                    page.click(selector)
                    page.keyboard.type(text, delay=110) # 110ms İnsansı gecikme
                    time.sleep(3)
                    if i < len(tweets) - 1:
                        for _ in range(11 if i==0 else 10): 
                            page.keyboard.press("Tab"); time.sleep(0.5)
                        page.keyboard.press("Enter"); time.sleep(6)
                time.sleep(4); page.keyboard.press("Control+Enter")
                time.sleep(8); context.close()
                if media_path and os.path.exists(media_path): os.remove(media_path)
                return "Başarılı"
            except Exception as e: return str(e)

    # --- 6. İSTİHBARAT ---
    def get_user_latest_tweet(self, username):
        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(self.user_data_dir, headless=False)
                page = context.new_page()
                page.goto(f"https://x.com/{username}")
                time.sleep(5)
                tweet = page.locator('article[data-testid="tweet"]').first
                links = tweet.locator('a[href*="/status/"]').first
                url = f"https://x.com{links.get_attribute('href')}"
                res = {"text": tweet.inner_text().replace('\n', ' '), "url": url}
                context.close(); return res
            except Exception as e: return str(e)

    def like_and_reply(self, tweet_url, reply_text):
        """Beğeni ve yorum yapar - İnsansı Tempo."""
        with sync_playwright() as p:
            try:
                context = p.chromium.launch_persistent_context(self.user_data_dir, headless=False)
                page = context.new_page()
                page.goto(tweet_url, wait_until="domcontentloaded")
                time.sleep(7)
                time.sleep(2); page.locator('button[data-testid="like"]').first.click()
                time.sleep(3); page.locator('div[data-testid="tweetTextarea_0"]').first.click()
                page.keyboard.type(reply_text, delay=120) # 120ms İnsansı gecikme
                time.sleep(4); page.keyboard.press("Control+Enter")
                time.sleep(6); context.close(); return "Başarılı"
            except Exception as e: return str(e)

    # --- 7. VİDEO ATÖLYESİ ---
    def create_shorts_video(self, text, topic_name):
        try:
            audio_path = os.path.join(self.user_data_dir, "ses.mp3")
            video_path = os.path.join(os.getcwd(), f"{topic_name.replace(' ', '_')}.mp4")
            bg_image_path = os.path.join(os.getcwd(), "arkaplan.jpg") 
            if not os.path.exists(bg_image_path): return "Hata: arkaplan.jpg yok"
            communicate = edge_tts.Communicate(text, "tr-TR-AhmetNeural")
            asyncio.run(communicate.save(audio_path))
            audio_clip = AudioFileClip(audio_path)
            video = ImageClip(bg_image_path).with_duration(audio_clip.duration).with_audio(audio_clip)
            video.write_videofile(video_path, fps=24, codec="libx264", logger=None)
            audio_clip.close(); os.remove(audio_path); return video_path
        except Exception as e: return str(e)

    # --- 8. 4060 Ti ÇİZİM MOTORU ---
    def generate_image(self, prompt):
        """404 hatası vermeyen SDXL-Turbo modeli."""
        print(f"🎨 [4060 Ti]: Çiziliyor -> {prompt}")
        try:
            import torch
            from diffusers import AutoPipelineForText2Image
            model_id = "stabilityai/sdxl-turbo"
            pipe = AutoPipelineForText2Image.from_pretrained(model_id, torch_dtype=torch.float16, variant="fp16").to("cuda")
            image = pipe(prompt=prompt, num_inference_steps=2, guidance_scale=0.0).images[0]
            path = os.path.join(os.getcwd(), 'ahmet_yerel_tasarim.jpg')
            image.save(path); del pipe; torch.cuda.empty_cache(); return path
        except Exception as e: return f"Hata: {str(e)}"