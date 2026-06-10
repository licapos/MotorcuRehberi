import streamlit as st
import requests
import urllib.parse

# ================= AYARLAR =================
STRAPI_URL = "https://motorcu-backend.onrender.com/api/cities"

# BURAYA STRAPI'DEN ALDIĞIN UZUN API TOKEN'INI YAPIŞTIR:
STRAPI_API_KEY = "5aa3724f06753541c0f53f014b65cb32060d92be8df3aae761e3a8698677b6e3e077b92f5cb677e7b76e6f88a9627fec4c21caa6d7182006f2ada223e3741600fa115358bd28040d104b4397c851e169bd79d338029ff62f936d97cf93d4f976061114cefd3a5f327fcf3990cba2efee2454d9cec628d53822adca13d932e480" 

HEADERS = {
    "Authorization": f"Bearer {STRAPI_API_KEY}",
    "Content-Type": "application/json"
}
# ============================================

st.set_page_config(page_title="Motorcu Rehberi", page_icon="🏍️")

st.title("🏍️ Yapay Zeka Destekli Motorcu Rehberi")
st.write("Aşağıdaki rotaların görselleri, veritabanından (Strapi) gelen metinlere göre Yapay Zeka tarafından anlık olarak çizilmektedir.")

# 1. Strapi'den Şehirleri Çekme Fonksiyonu
def sehirleri_cek():
    try:
        cevap = requests.get(STRAPI_URL, headers=HEADERS)
        if cevap.status_code == 200:
            # Strapi v4 yapısına göre veriyi alıyoruz
            return cevap.json().get("data", [])
        else:
            st.error(f"API Bağlantı Hatası (Kod: {cevap.status_code})")
            return []
    except Exception as e:
        st.error(f"Sunucuya bağlanılamadı: {e}")
        return []

veriler = sehirleri_cek()

# 2. Arayüz ve Yapay Zeka (AI) Görselleştirme
if veriler:
    for sehir in veriler:
        # Strapi'deki alanın adı 'Ad' olarak varsayıldı. Eğer panelde 'Name' yaptıysan burayı 'Name' olarak değiştir.
        sehir_adi = sehir["attributes"]["Ad"]
        
        st.subheader(f"📍 Rota: {sehir_adi}")
        
        with st.spinner(f"Yapay Zeka '{sehir_adi}' için çalışıyor..."):
            # AI Prompt'u hazırlıyoruz (Motorcu temalı)
            prompt = f"A cool motorcycle riding on {sehir_adi}, epic landscape, photorealistic, 8k resolution, cinematic lighting"
            encoded_prompt = urllib.parse.quote(prompt)
            
            # Ücretsiz, key gerektirmeyen görsel AI servisi
            ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}"
            
            # Resmi ve bilgiyi ekrana basıyoruz
            st.image(ai_image_url, caption=f"Yapay Zeka Üretimi: {sehir_adi}", use_container_width=True)
            st.markdown("---")
else:
    st.warning("Veritabanından rota bulunamadı. Lütfen panelden şehir ekleyip 'Publish' yaptığınızdan emin olun.")