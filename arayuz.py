import streamlit as st
import requests

# ================= AYARLAR =================
STRAPI_URL = "https://motorcu-api.onrender.com/api"
# ============================================

st.set_page_config(page_title="Motorcu Gezi Rehberi", page_icon="🏍️", layout="centered")

# Ozel CSS
st.markdown("""
<style>
    .sub-text {text-align:center;color:#aaa;font-size:1rem;margin-bottom:2rem}
    .rota-bilgi {
        font-size:1.05rem;color:#ddd;line-height:1.8;margin:12px 0;padding:16px;
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:12px;border-left:4px solid #e94560;
    }
    .mekan-card {
        background:linear-gradient(135deg,#0f0f23,#1a1a3e);
        border-radius:14px;padding:20px;margin:16px 0;
        border:1px solid #ffffff10;
    }
    .mekan-baslik {font-size:1.3rem;font-weight:bold;color:#e94560;margin-bottom:4px}
    .puan-badge {
        display:inline-block;background:#e94560;color:white;
        padding:4px 12px;border-radius:20px;font-size:0.85rem;font-weight:bold;
    }
    .footer-text {text-align:center;color:#666;font-size:.85rem;margin-top:2rem;padding:16px}
</style>
""", unsafe_allow_html=True)

st.title("🏍️ Motorcu Gezi Rehberi")
st.markdown('<p class="sub-text">Bir şehir seçin, o şehirdeki mekânları YZ görselleriyle keşfedin!</p>', unsafe_allow_html=True)


# Sehirleri Cek (hem tr hem en locale dene)
@st.cache_data(ttl=60)
def sehirleri_cek():
    try:
        cevap = requests.get(f"{STRAPI_URL}/cities?locale=tr", timeout=30)
        if cevap.status_code == 200:
            return cevap.json().get("data", [])
        return []
    except Exception as e:
        st.error(f"Sunucuya baglanamadi: {e}")
        return []


# Mekanlari Cek
@st.cache_data(ttl=60)
def tum_mekanlari_cek():
    try:
        # Tum mekanlari cek (tr locale)
        url = f"{STRAPI_URL}/places?populate=KapakResmi,city&locale=tr&pagination[pageSize]=100"
        cevap = requests.get(url, timeout=30)
        if cevap.status_code == 200:
            return cevap.json().get("data", [])
        return []
    except Exception:
        return []


# Strapi Media URL olustur
def gorsel_url_al(mekan):
    try:
        kapak = mekan.get("KapakResmi")
        if kapak:
            img_url = kapak.get("url", "")
            if img_url:
                if img_url.startswith("/"):
                    return f"https://motorcu-api.onrender.com{img_url}"
                return img_url
    except Exception:
        pass
    return None


# Mekan-sehir eslesme (isimlere gore)
MEKAN_SEHIR = {
    "Olimpos Antik Kenti": "Antalya",
    "Kas Marina": "Antalya",
    "Demre Myra Antik Kenti": "Antalya",
    "Grand Canyon": "Route 66",
    "Cadillac Ranch": "Route 66",
    "Santa Monica Pier": "Route 66",
}


# Ana Akis
veriler = sehirleri_cek()
tum_mekanlar = tum_mekanlari_cek()

if veriler:
    sehir_isimleri = []
    sehir_map = {}
    for sehir in veriler:
        ad = sehir.get("Ad", "Bilinmeyen")
        sehir_isimleri.append(ad)
        sehir_map[ad] = sehir

    secilen_sehir_adi = st.selectbox("🌍 Şehir Seçin:", options=sehir_isimleri, index=0)
    st.markdown("---")

    if secilen_sehir_adi:
        secilen_sehir = sehir_map[secilen_sehir_adi]
        sehir_doc_id = secilen_sehir.get("documentId")

        st.header(f"📍 {secilen_sehir_adi}")

        ulke = secilen_sehir.get("Ulke")
        if ulke:
            st.caption(f"🌍 Ülke: **{ulke}**")

        kisa_bilgi = secilen_sehir.get("KisaBilgi")
        if kisa_bilgi and isinstance(kisa_bilgi, str) and kisa_bilgi.strip():
            st.markdown(f'<div class="rota-bilgi">{kisa_bilgi}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Mekanlari filtrele: city iliskisi varsa ona gore, yoksa isim eslesmesi ile
        filtreli_mekanlar = []
        for mekan in tum_mekanlar:
            mekan_adi = mekan.get("MekanAdi", "")
            # City iliskisi var mi kontrol et
            city_rel = mekan.get("city")
            if city_rel and city_rel.get("documentId") == sehir_doc_id:
                filtreli_mekanlar.append(mekan)
            elif not city_rel:
                # Isim eslesmesi ile kontrol et
                for anahtar, sehir_kismi in MEKAN_SEHIR.items():
                    if anahtar in mekan_adi and sehir_kismi in secilen_sehir_adi:
                        filtreli_mekanlar.append(mekan)
                        break

        if filtreli_mekanlar:
            st.subheader(f"🏛️ Mekânlar ({len(filtreli_mekanlar)} adet)")
            st.markdown("")

            for mekan in filtreli_mekanlar:
                mekan_adi = mekan.get("MekanAdi", "Bilinmeyen Mekan")
                aciklama = mekan.get("Aciklama", "")
                puan = mekan.get("Puan", 0)

                st.markdown(f'<div class="mekan-baslik">📌 {mekan_adi}</div>', unsafe_allow_html=True)

                if puan:
                    st.markdown(f'<span class="puan-badge">⭐ {puan}/5</span>', unsafe_allow_html=True)

                # Kapak resmi (Strapi Media Library'den)
                gorsel_url = gorsel_url_al(mekan)
                if gorsel_url:
                    st.image(gorsel_url, caption=f"🤖 YZ Üretimi: {mekan_adi}", use_container_width=True)

                # Aciklama (TR + EN birlesik)
                if aciklama:
                    if "[EN]" in aciklama:
                        parcalar = aciklama.split("[EN]")
                        st.markdown(f"**🇹🇷 Türkçe:** {parcalar[0].strip()}")
                        st.markdown(f"**🇬🇧 English:** {parcalar[1].strip()}")
                    else:
                        st.markdown(f"**📝 Açıklama:** {aciklama}")

                st.markdown("---")
        else:
            st.info("Bu şehir için henüz mekân eklenmemiş. Otomasyon scriptini çalıştırarak mekân ekleyebilirsiniz.")

    st.markdown('<p class="footer-text">🏍️ Motorcu Gezi Rehberi — YZ Destekli Gezi Platformu 🛣️</p>', unsafe_allow_html=True)

else:
    st.warning("Şehir bulunamadı. Strapi backend'in çalıştığından emin olun.")
