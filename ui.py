import streamlit as st
from agent.core import Agent
import time

# Sayfa Ayarları
st.set_page_config(page_title="Gemini Ajanı", page_icon="🤖", layout="centered")

# CSS ile biraz yakışıklılık katalım (Beşiktaş renkleri ve modern görünüm)
st.markdown("""
    <style>
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .stApp { background-color: #f5f7f9; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Gemini Kişisel Asistan")
st.caption("Mami Dayı'nın Sadık Asistanı | Hafızalı ve İnternet Destekli")

# Ajanı başlat (Session State kullanarak her yenilemede sıfırlanmasını önlüyoruz)
if "agent" not in st.session_state:
    st.session_state.agent = Agent()
    st.session_state.messages = []

# Eski mesajları ekrana bas
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Kullanıcı girişi
if prompt := st.chat_input("Reis, ne yapalım bugün?"):
    # 1. Kullanıcı mesajını göster ve kaydet
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Asistanın cevabını al
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        # Ajanı çalıştır
        with st.spinner("Düşünüyorum dayı..."):
            try:
                response = st.session_state.agent.run(prompt)
                
                # Yazma efekti (Simüle edilmiş)
                for chunk in response.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Bir sorun çıktı dayı: {e}")
                full_response = "Kusura bakma dayı, bir hata oluştu."

    # 3. Asistan cevabını kaydet
    st.session_state.messages.append({"role": "assistant", "content": full_response})