import streamlit as st
import requests
import urllib.parse

# ================= AYARLAR =================
STRAPI_URL = "https://motorcu-backend.onrender.com/api/cities"

# BURAYA STRAPI'DEN ALDIĞIN UZUN API TOKEN'INI YAPIŞTIR:
STRAPI_API_KEY = "86fe39d30c1c14bcddc8cf8dab542de329da9539f2439767380e9a4201d9a2998796e76495de80e630ffc6601adff09d494012e27210ddc48703a49406270b1344543058721d0336b568ac8934ca2c83d8f1f8d513b7eb32c3e32313a8a935908af98aeb745f78e45fcdceec9d17853b342e96fa2800f915bb80e72ce885f4ce" 

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