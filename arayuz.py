import streamlit as st
import requests
import urllib.parse
# ================= AYARLAR =================
# Public izinler açık olduğu için token'a gerek yok
STRAPI_URL = "https://motorcu-api.onrender.com/api/cities"
# ============================================
st.set_page_config(page_title="Motorcu Rehberi", page_icon="🏍️")
st.title("Motorcu Gezi Rehberi")
# 1. Strapi'den Şehirleri Çekme Fonksiyonu
def sehirleri_cek():
    try:
        # Public erişim açık, token göndermeden istek atıyoruz
        cevap = requests.get(STRAPI_URL)
        if cevap.status_code == 200:
            # Strapi v5 yapısına göre veriyi alıyoruz
            return cevap.json().get("data", [])
        else:
            st.error(f"API Bağlantı Hatası (Kod: {cevap.status_code})")
            try:
                st.code(cevap.text[:500])
            except Exception:
                pass
            return []
    except Exception as e:
        st.error(f"Sunucuya bağlanılamadı: {e}")
        return []
veriler = sehirleri_cek()
# 2. Arayüz ve Yapay Zeka (AI) Görselleştirme
if veriler:
    for sehir in veriler:
        # Strapi v5'te "attributes" sarmalayıcısı kaldırıldı,
        # veriler doğrudan nesnenin içinde geliyor.
        sehir_adi = sehir.get("Ad") or sehir.get("attributes", {}).get("Ad", "Bilinmeyen Rota")
        
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
