import streamlit as st
import requests
import urllib.parse
# ================= AYARLAR =================
# ÖNEMLİ: URL'yi kendi Render backend adresinle eşleştir
STRAPI_URL = "https://motorcu-api.onrender.com/api/cities"
# BURAYA STRAPI'DEN ALDIĞIN UZUN API TOKEN'INI YAPIŞTIR:
STRAPI_API_KEY = "41506efe63774ce97ca51606fe08f903d36090939a982c42e4080f07797c07fad7720f669888121c4090ac67fbd3f4e99cf4cc097555b42b703a9ce7587bcb80df2f019a01757bfccfac9cad804054f7819a950122451ab91cf1ff8d7c8f4af8f77c90618ea613e89f81171b61fb2d1c99d490415f38c5d16c14afc72ba90fcb" 
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
            # Strapi v5 yapısına göre veriyi alıyoruz
            return cevap.json().get("data", [])
        else:
            st.error(f"API Bağlantı Hatası (Kod: {cevap.status_code})")
            # Hata detayını da gösterelim (debug için)
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
