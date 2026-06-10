# streamlit ile frontend arayuzu
# strapi'den sehir ve mekan verilerini cekip gosteriyor
import streamlit as st
import requests

STRAPI_URL = "https://motorcu-api.onrender.com/api"

st.set_page_config(page_title="Motorcu Gezi Rehberi", page_icon="🏍️", layout="centered")

# sayfa tasarimi icin css
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Outfit', sans-serif; }
    
    .hero-title {
        text-align:center; font-size:2.6rem; font-weight:700;
        background: linear-gradient(135deg, #ff6b6b, #ffa500, #ff6b6b);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .hero-sub {
        text-align:center; color:#888; font-size:1rem; margin-bottom:2rem;
        font-weight:300; letter-spacing:0.5px;
    }
    .city-header {
        font-size:2rem; font-weight:600; color:#fff;
        border-bottom: 2px solid #ff6b6b; padding-bottom:8px; margin-bottom:4px;
    }
    .ulke-tag {
        display:inline-block; background:linear-gradient(135deg,#ff6b6b,#ee5a24);
        color:white; padding:4px 14px; border-radius:20px; font-size:0.8rem;
        font-weight:500; letter-spacing:0.5px;
    }
    .bilgi-box {
        background: linear-gradient(135deg, #1e1e3f 0%, #2d1b4e 100%);
        border-radius:16px; padding:20px; margin:16px 0;
        border-left: 4px solid #ff6b6b; color:#ddd; line-height:1.7;
        font-size:1rem;
    }
    .place-name {
        font-size:1.4rem; font-weight:600; 
        background: linear-gradient(90deg, #ff6b6b, #ffa500);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin:0; padding:0;
    }
    .score {
        display:inline-block; background:linear-gradient(135deg,#ff6b6b,#ee5a24);
        color:white; padding:5px 14px; border-radius:24px;
        font-size:0.85rem; font-weight:600; margin:6px 0 12px 0;
    }
    .desc-block {
        background:#ffffff08; border-radius:12px; padding:14px 18px;
        margin:8px 0 6px 0; color:#ccc; line-height:1.6; font-size:0.95rem;
    }
    .desc-label { font-weight:600; color:#ff6b6b; font-size:0.85rem; margin-bottom:4px; }
    .divider { border:none; border-top:1px solid #ffffff10; margin:24px 0; }
    .footer {
        text-align:center; color:#555; font-size:0.8rem;
        margin-top:3rem; padding:20px; border-top:1px solid #ffffff08;
    }
</style>
""", unsafe_allow_html=True)

# baslik
st.markdown('<div class="hero-title">🏍️ Motorcu Gezi Rehberi</div>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">Keşfedilecek rotalar, görülecek yerler</p>', unsafe_allow_html=True)


# sehirleri strapi'den cek
@st.cache_data(ttl=60)
def sehirleri_getir():
    try:
        r = requests.get(f"{STRAPI_URL}/cities?locale=tr", timeout=30)
        return r.json().get("data", []) if r.status_code == 200 else []
    except:
        return []


# mekanlari strapi'den cek
@st.cache_data(ttl=60)
def mekanlari_getir():
    try:
        r = requests.get(f"{STRAPI_URL}/places?populate=KapakResmi&locale=tr&pagination[pageSize]=100", timeout=30)
        return r.json().get("data", []) if r.status_code == 200 else []
    except:
        return []


# kapak resminin url'sini al
def resim_url(mekan):
    try:
        kapak = mekan.get("KapakResmi")
        if kapak:
            url = kapak.get("url", "")
            if url.startswith("/"):
                return f"https://motorcu-api.onrender.com{url}"
            return url
    except:
        pass
    return None


# hangi mekan hangi sehre ait (isim eslemesi)
MEKAN_ESLEME = {
    "Olimpos Antik Kenti": "Antalya",
    "Kas Marina": "Antalya",
    "Demre Myra Antik Kenti": "Antalya",
    "Grand Canyon": "Route 66",
    "Cadillac Ranch": "Route 66",
    "Santa Monica Pier": "Route 66",
}

# verileri cek
sehirler = sehirleri_getir()
mekanlar = mekanlari_getir()

if sehirler:
    # sehir secimi
    sehir_adlari = [s.get("Ad", "?") for s in sehirler]
    sehir_map = {s.get("Ad", "?"): s for s in sehirler}

    secim = st.selectbox("🌍 Şehir Seçin", options=sehir_adlari, index=0)
    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    if secim:
        sehir = sehir_map[secim]

        # sehir bilgileri
        st.markdown(f'<div class="city-header">📍 {secim}</div>', unsafe_allow_html=True)
        
        ulke = sehir.get("Ulke", "")
        if ulke:
            st.markdown(f'<span class="ulke-tag">{ulke}</span>', unsafe_allow_html=True)

        bilgi = sehir.get("KisaBilgi", "")
        if bilgi and isinstance(bilgi, str) and bilgi.strip():
            st.markdown(f'<div class="bilgi-box">{bilgi}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # secilen sehre ait mekanlari filtrele
        sehir_mekanlari = []
        for m in mekanlar:
            isim = m.get("MekanAdi", "")
            for anahtar, hedef in MEKAN_ESLEME.items():
                if anahtar in isim and hedef in secim:
                    sehir_mekanlari.append(m)
                    break

        if sehir_mekanlari:
            st.markdown(f"### 🏛️ Görülecek Yerler")

            for m in sehir_mekanlari:
                isim = m.get("MekanAdi", "")
                aciklama = m.get("Aciklama", "")
                puan = m.get("Puan", 0)

                st.markdown(f'<div class="place-name">{isim}</div>', unsafe_allow_html=True)

                if puan:
                    st.markdown(f'<span class="score">⭐ {puan}/5</span>', unsafe_allow_html=True)

                # kapak resmi
                url = resim_url(m)
                if url:
                    st.image(url, use_container_width=True)

                # aciklama (turkce ve ingilizce ayri goster)
                if aciklama:
                    if "[EN]" in aciklama:
                        parcalar = aciklama.split("[EN]")
                        st.markdown(f'<div class="desc-label">🇹🇷 Türkçe</div><div class="desc-block">{parcalar[0].strip()}</div>', unsafe_allow_html=True)
                        st.markdown(f'<div class="desc-label">🇬🇧 English</div><div class="desc-block">{parcalar[1].strip()}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="desc-block">{aciklama}</div>', unsafe_allow_html=True)

                st.markdown('<hr class="divider">', unsafe_allow_html=True)
        else:
            st.info("Bu rota için henüz mekân eklenmemiş.")

    st.markdown('<div class="footer">Motorcu Gezi Rehberi © 2025</div>', unsafe_allow_html=True)
else:
    st.warning("Veriler yüklenemedi. Backend çalışıyor mu kontrol edin.")
