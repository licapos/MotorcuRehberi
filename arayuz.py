import streamlit as st
import requests
import urllib.parse
# ================= AYARLAR =================
STRAPI_URL = "https://motorcu-api.onrender.com/api/cities"
# ============================================
st.set_page_config(page_title="Motorcu Rehberi", page_icon="🏍️", layout="centered")
st.title("Motorcu Gezi Rehberi")
# 1. Strapi'den Şehirleri Çekme Fonksiyonu
@st.cache_data(ttl=60)
def sehirleri_cek():
    try:
        cevap = requests.get(STRAPI_URL)
        if cevap.status_code == 200:
            return cevap.json().get("data", [])
        else:
            st.error(f"API Bağlantı Hatası (Kod: {cevap.status_code})")
            return []
    except Exception as e:
        st.error(f"Sunucuya bağlanılamadı: {e}")
        return []
veriler = sehirleri_cek()
# 2. Arayüz
if veriler:
    # Rota isimlerini çıkar
    rota_isimleri = []
    for sehir in veriler:
        ad = sehir.get("Ad") or sehir.get("attributes", {}).get("Ad", "Bilinmeyen Rota")
        rota_isimleri.append(ad)
    # Dropdown menü ile rota seçimi
    secilen_rota = st.selectbox(
        "📍 Rota Seçin:",
        options=rota_isimleri,
        index=0
    )
    st.markdown("---")
    # Seçilen rota için AI görsel oluştur
    if secilen_rota:
        st.subheader(f"🏍️ {secilen_rota}")
        with st.spinner(f"Yapay Zeka '{secilen_rota}' için görsel üretiyor... (10-20 saniye sürebilir)"):
            # Prompt oluştur
            prompt = f"A cool motorcycle riding on {secilen_rota}, epic landscape, photorealistic, 8k resolution, cinematic lighting"
            
            # Boşlukları + ile değiştir (Pollinations API formatı)
            encoded_prompt = prompt.replace(" ", "+")
            
            # Pollinations AI görsel URL'si
            ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true"
            # Görseli requests ile indir, sonra Streamlit'te göster
            try:
                img_response = requests.get(ai_image_url, timeout=60)
                if img_response.status_code == 200:
                    st.image(img_response.content, caption=f"🤖 Yapay Zeka Üretimi: {secilen_rota}", use_container_width=True)
                else:
                    st.error(f"Görsel oluşturulamadı (Kod: {img_response.status_code})")
            except requests.exceptions.Timeout:
                st.warning("Görsel oluşturma zaman aşımına uğradı. Lütfen tekrar deneyin.")
            except Exception as e:
                st.error(f"Görsel yüklenirken hata oluştu: {e}")
        st.markdown("---")
        st.caption("Bu görsel yapay zeka tarafından anlık olarak üretilmiştir. Her yenilemede farklı bir görsel oluşturulur.")
else:
    st.warning("Veritabanından rota bulunamadı. Lütfen panelden şehir ekleyip 'Publish' yaptığınızdan emin olun.")