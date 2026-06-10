import streamlit as st
import requests

# ================= AYARLAR =================
# locale=en eklendi çünkü rotalar English locale ile oluşturulmuş
STRAPI_URL = "https://motorcu-api.onrender.com/api/cities?locale=en"
# ============================================

st.set_page_config(page_title="Motorcu Rehberi", page_icon="🏍️", layout="centered")

# Özel CSS
st.markdown("""
<style>
    .sub-text {text-align:center;color:#aaa;font-size:1rem;margin-bottom:2rem}
    .rota-bilgi {
        font-size:1.05rem;color:#ddd;line-height:1.8;margin:12px 0;padding:16px;
        background:linear-gradient(135deg,#1a1a2e,#16213e);
        border-radius:12px;border-left:4px solid #e94560;
    }
    .footer-text {text-align:center;color:#666;font-size:.85rem;margin-top:2rem;padding:16px}
</style>
""", unsafe_allow_html=True)

st.title("🏍️ Motorcu Gezi Rehberi")
st.markdown('<p class="sub-text">Bir rota seçin, detaylı bilgi ve görseller ile keşfedin!</p>', unsafe_allow_html=True)

# ========== ROTA BİLGİLERİ ==========
ROTA_BILGILERI = {
    "Antalya - Kaş Sahil Yolu": {
        "aciklama": "Türkiye'nin en güzel sahil yollarından biri olan Antalya-Kaş rotası, Akdeniz'in turkuaz sularına karşı muhteşem virajlarıyla motosiklet tutkunlarının vazgeçilmezi.",
        "mesafe": "230 km", "sure": "~4 saat", "zorluk": "⭐⭐⭐ Orta",
        "en_iyi_sezon": "Nisan - Kasım",
        "dikkat": "Virajlı yollar ve dik iniş-çıkışlar mevcut. Dikkatli sürüş önerilir.",
        "gorulen_yerler": "Olimpos, Çıralı, Demre, Myra Antik Kenti, Kaş Marina",
        "gorsel": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=1200&h=700&fit=crop",
    },
    "Route 66": {
        "aciklama": "Dünyanın en ikonik motosiklet rotası! Chicago'dan Los Angeles'a uzanan efsanevi Route 66, Amerikan rüyasının asfalt üzerindeki yansıması.",
        "mesafe": "3.940 km", "sure": "~2-3 hafta", "zorluk": "⭐⭐ Kolay-Orta",
        "en_iyi_sezon": "Mayıs - Ekim",
        "dikkat": "Uzun mesafe için iyi bir planlama ve dinlenme molaları şart.",
        "gorulen_yerler": "Grand Canyon, Cadillac Ranch, Santa Monica Pier, Painted Desert",
        "gorsel": "https://images.unsplash.com/photo-1545063328-c8e4e0da3e11?w=1200&h=700&fit=crop",
    },
}

VARSAYILAN = {
    "aciklama": "Motosikletle keşfedilmeyi bekleyen harika bir rota!",
    "mesafe": "—", "sure": "—", "zorluk": "—", "en_iyi_sezon": "—",
    "dikkat": "Güvenli sürüş kurallarına uyunuz.", "gorulen_yerler": "—",
    "gorsel": "https://images.unsplash.com/photo-1449426468159-d96dbf08f19f?w=1200&h=700&fit=crop",
}


# 1. Strapi'den Şehirleri Çek
@st.cache_data(ttl=60)
def sehirleri_cek():
    try:
        cevap = requests.get(STRAPI_URL)
        if cevap.status_code == 200:
            return cevap.json().get("data", [])
        else:
            st.error(f"API Hatası (Kod: {cevap.status_code})")
            return []
    except Exception as e:
        st.error(f"Sunucuya bağlanılamadı: {e}")
        return []


veriler = sehirleri_cek()

# 2. Arayüz
if veriler:
    rota_isimleri = []
    for sehir in veriler:
        ad = sehir.get("Ad") or sehir.get("attributes", {}).get("Ad", "Bilinmeyen Rota")
        rota_isimleri.append(ad)

    secilen_rota = st.selectbox("📍 Rota Seçin:", options=rota_isimleri, index=0)
    st.markdown("---")

    if secilen_rota:
        bilgi = ROTA_BILGILERI.get(secilen_rota, VARSAYILAN)

        # Strapi'den gelen ek bilgiler
        secilen_veri = None
        for sehir in veriler:
            ad = sehir.get("Ad") or sehir.get("attributes", {}).get("Ad", "")
            if ad == secilen_rota:
                secilen_veri = sehir
                break

        # Başlık
        st.header(f"🏍️ {secilen_rota}")

        # Ülke bilgisi (Strapi'den)
        if secilen_veri and secilen_veri.get("Ulke"):
            st.caption(f"🌍 Ülke: **{secilen_veri['Ulke']}**")

        # Açıklama
        st.markdown(f'<div class="rota-bilgi">{bilgi["aciklama"]}</div>', unsafe_allow_html=True)

        # Görsel — Unsplash CDN, API çağrısı yok, kesin çalışır
        st.image(bilgi["gorsel"], caption=f"📸 {secilen_rota}", use_container_width=True)

        # Bilgi kartları
        st.markdown("")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📏 Mesafe", bilgi["mesafe"])
        with col2:
            st.metric("⏱️ Süre", bilgi["sure"])
        with col3:
            st.metric("💪 Zorluk", bilgi["zorluk"])

        # Detaylar
        st.markdown("")
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"**🗓️ En İyi Sezon**\n\n{bilgi['en_iyi_sezon']}\n\n**⚠️ Dikkat**\n\n{bilgi['dikkat']}")
        with col_b:
            st.markdown(f"**🏛️ Görülmesi Gereken Yerler**\n\n{bilgi['gorulen_yerler']}")

        st.markdown("---")
        st.markdown('<p class="footer-text">🏍️ Motorcu Gezi Rehberi — Güvenli sürüşler dileriz! 🛣️</p>', unsafe_allow_html=True)

else:
    st.warning("Rota bulunamadı. Panelden şehir ekleyip 'Publish' yapın.")
