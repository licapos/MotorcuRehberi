import streamlit as st
import requests

# ================= AYARLAR =================
STRAPI_URL = "https://motorcu-api.onrender.com/api"
# ============================================

st.set_page_config(page_title="Motorcu Gezi Rehberi", page_icon="🏍️", layout="centered")

# Özel CSS
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


# 1. Strapi'den Şehirleri Çek
@st.cache_data(ttl=60)
def sehirleri_cek():
    try:
        cevap = requests.get(f"{STRAPI_URL}/cities?locale=en", timeout=30)
        if cevap.status_code == 200:
            return cevap.json().get("data", [])
        else:
            st.error(f"Şehir API Hatası (Kod: {cevap.status_code})")
            return []
    except Exception as e:
        st.error(f"Sunucuya bağlanılamadı: {e}")
        return []


# 2. Strapi'den Mekanları Çek (şehre göre filtrelenmiş)
@st.cache_data(ttl=60)
def mekanlari_cek(sehir_doc_id):
    try:
        # Mekânları şehre göre filtrele + kapak resmini getir
        url = f"{STRAPI_URL}/places?filters[city][documentId][$eq]={sehir_doc_id}&populate=KapakResmi,city&locale=tr"
        cevap = requests.get(url, timeout=30)
        if cevap.status_code == 200:
            return cevap.json().get("data", [])
        else:
            return []
    except Exception:
        return []


# 3. Strapi Media URL oluştur
def gorsel_url_al(mekan):
    """Mekân verisinden kapak resmi URL'sini çıkarır"""
    try:
        kapak = mekan.get("KapakResmi")
        if kapak:
            # Strapi v5 yapısı
            img_url = kapak.get("url", "")
            if img_url:
                # Eğer relative URL ise tam URL oluştur
                if img_url.startswith("/"):
                    return f"https://motorcu-api.onrender.com{img_url}"
                return img_url
    except Exception:
        pass
    return None


# Ana Akış
veriler = sehirleri_cek()

if veriler:
    # Şehir isimlerini çıkar
    sehir_isimleri = []
    sehir_map = {}
    for sehir in veriler:
        ad = sehir.get("Ad", "Bilinmeyen")
        sehir_isimleri.append(ad)
        sehir_map[ad] = sehir

    # Şehir seçimi
    secilen_sehir_adi = st.selectbox("🌍 Şehir Seçin:", options=sehir_isimleri, index=0)
    st.markdown("---")

    if secilen_sehir_adi:
        secilen_sehir = sehir_map[secilen_sehir_adi]
        sehir_doc_id = secilen_sehir.get("documentId")

        # Şehir başlığı
        st.header(f"📍 {secilen_sehir_adi}")

        # Ülke bilgisi
        ulke = secilen_sehir.get("Ulke")
        if ulke:
            st.caption(f"🌍 Ülke: **{ulke}**")

        # Kısa bilgi
        kisa_bilgi = secilen_sehir.get("KisaBilgi")
        if kisa_bilgi and isinstance(kisa_bilgi, str) and kisa_bilgi.strip():
            st.markdown(f'<div class="rota-bilgi">{kisa_bilgi}</div>', unsafe_allow_html=True)

        st.markdown("---")

        # Mekânları getir
        if sehir_doc_id:
            mekanlar = mekanlari_cek(sehir_doc_id)

            if mekanlar:
                st.subheader(f"🏛️ Mekânlar ({len(mekanlar)} adet)")
                st.markdown("")

                for mekan in mekanlar:
                    mekan_adi = mekan.get("MekanAdi", "Bilinmeyen Mekân")
                    aciklama = mekan.get("Aciklama", "")
                    aciklama_en = mekan.get("AciklamaEN", "")
                    puan = mekan.get("Puan", 0)

                    # Mekân kartı
                    st.markdown(f'<div class="mekan-baslik">📌 {mekan_adi}</div>', unsafe_allow_html=True)

                    if puan:
                        st.markdown(f'<span class="puan-badge">⭐ {puan}/5</span>', unsafe_allow_html=True)

                    # Kapak resmi (Strapi Media Library'den)
                    gorsel_url = gorsel_url_al(mekan)
                    if gorsel_url:
                        st.image(gorsel_url, caption=f"🤖 YZ Üretimi: {mekan_adi}", use_container_width=True)

                    # Açıklama
                    if aciklama:
                        st.markdown(f"**🇹🇷 Türkçe:** {aciklama}")
                    if aciklama_en:
                        st.markdown(f"**🇬🇧 English:** {aciklama_en}")

                    st.markdown("---")
            else:
                st.info("Bu şehir için henüz mekân eklenmemiş. Otomasyon scriptini çalıştırarak mekân ekleyebilirsiniz.")

    st.markdown('<p class="footer-text">🏍️ Motorcu Gezi Rehberi — YZ Destekli Gezi Platformu 🛣️</p>', unsafe_allow_html=True)

else:
    st.warning("Şehir bulunamadı. Strapi backend'in çalıştığından emin olun.")
