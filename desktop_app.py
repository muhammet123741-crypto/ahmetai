import customtkinter as ctk
from agent.core import Agent
import threading
import uuid
import time
import json

class AhmetUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Ahmet v4.6 - Atakum Otonom Kontrol Merkezi")
        self.geometry("1150x800")
        self.agent = Agent()
        
        # Aktif Seans ID'si
        self.current_session_id = str(uuid.uuid4())[:8]

        # Grid Ayarları
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- SIDEBAR: GEÇMİŞ VE YENİ SOHBET ---
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.new_chat_btn = ctk.CTkButton(self.sidebar, text="+ Yeni Sohbet Başlat", 
                                          font=ctk.CTkFont(weight="bold"), command=self.new_chat)
        self.new_chat_btn.pack(pady=25, padx=20, fill="x")

        self.history_scroll = ctk.CTkScrollableFrame(self.sidebar, label_text="Geçmiş Muhabbetler")
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=10)

        # --- ANA SOHBET ALANI ---
        self.chat_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.chat_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.chat_frame.grid_rowconfigure(0, weight=1)
        self.chat_frame.grid_columnconfigure(0, weight=1)

        self.textbox = ctk.CTkTextbox(self.chat_frame, font=ctk.CTkFont(size=16), wrap="word", border_width=2)
        self.textbox.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        self.textbox.insert("0.0", "Ahmet: Selamün aleyküm Mami Dayı! Atakum'un havası gibi ferah bir arayüzle emrindeyim.\n")

        # Giriş Alanı
        self.entry_container = ctk.CTkFrame(self.chat_frame, fg_color="transparent")
        self.entry_container.grid(row=1, column=0, sticky="ew")
        self.entry_container.grid_columnconfigure(0, weight=1)

        self.entry = ctk.CTkEntry(self.entry_container, placeholder_text="Buraya yaz dayı...", height=50, font=ctk.CTkFont(size=16))
        self.entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(self.entry_container, text="GÖNDER", width=120, height=50, command=self.send_message)
        self.send_btn.grid(row=0, column=1)

        self.refresh_history()

    def new_chat(self):
        """Eski seansı kapatır, yeni bir ID ile temiz sayfa açar."""
        self.current_session_id = str(uuid.uuid4())[:8]
        self.textbox.delete("0.0", "end")
        self.textbox.insert("end", f"Ahmet: Yeni bir seans başladı dayı. (ID: {self.current_session_id})\n" + "-"*30 + "\n")

    def refresh_history(self):
        """Hafızadaki seansları sol tarafa tarihleriyle dizer."""
        for widget in self.history_scroll.winfo_children(): widget.destroy()
        
        data = self.agent.memory.load_memory()
        sessions = data.get("sessions", {})

        # En yeni seans en üstte
        for sid, info in reversed(list(sessions.items())):
            item_frame = ctk.CTkFrame(self.history_scroll, fg_color="transparent")
            item_frame.pack(fill="x", pady=5)
            
            # Tarih ve Başlık
            display_text = f"📅 {info['date']}\n{info['title']}"
            btn = ctk.CTkButton(item_frame, text=display_text, anchor="w", fg_color="transparent", 
                                hover_color="#333333", command=lambda s=sid: self.load_session(s))
            btn.pack(side="left", fill="x", expand=True)
            
            # Silme Butonu
            del_btn = ctk.CTkButton(item_frame, text="X", width=30, fg_color="#880000", 
                                    command=lambda s=sid: self.delete_session(s))
            del_btn.pack(side="right", padx=5)

    def load_session(self, sid):
        """Seçilen seansın tüm konuşmalarını ekrana basar."""
        self.current_session_id = sid
        self.textbox.delete("0.0", "end")
        data = self.agent.memory.load_memory()
        session = data["sessions"].get(sid, {})
        
        self.textbox.insert("end", f"📅 [GEÇMİŞ SOHBET: {session.get('date')}]\n" + "="*40 + "\n")
        for msg in session.get("messages", []):
            self.textbox.insert("end", f"\nMami Dayı: {msg['user']}\n")
            self.textbox.insert("end", f"\nAhmet: {msg['agent']}\n")
            self.textbox.insert("end", "-"*30 + "\n")
        self.textbox.see("end")

    def delete_session(self, sid):
        data = self.agent.memory.load_memory()
        if sid in data["sessions"]:
            del data["sessions"][sid]
            with open(self.agent.memory.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        self.refresh_history()

    def send_message(self):
        txt = self.entry.get()
        if not txt: return
        self.textbox.insert("end", f"\nMami Dayı: {txt}\n")
        self.entry.delete(0, "end")
        threading.Thread(target=self.run_agent, args=(txt,), daemon=True).start()

    def run_agent(self, txt):
        # Ahmet'in beyin fırtınası başlar
        response = self.agent.run(txt, self.current_session_id) 
        
        # BURASI KRİTİK: Hafızayı mühürlemeden önce agent'ın içindeki memory nesnesini kullanıyoruz
        try:
            self.agent.memory.save_interaction(self.current_session_id, txt, response)
        except Exception as e:
            print(f"Hafıza mühürlenirken pürüz çıktı: {e}")
            
        self.textbox.insert("end", f"\nAhmet: {response}\n")
        self.textbox.see("end")
        self.after(100, self.refresh_history)

if __name__ == "__main__":
    app = AhmetUI()
    app.mainloop()