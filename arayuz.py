import streamlit as st
import requests

STRAPI_URL = "https://motorcu-backend.onrender.com"
STRAPI_TOKEN = "f3f9cae16285feee9bfd20a29c0cbc022b6ed87fbaefe2a97f13bbc447c038fd4591440d1543293f85b494f37614d677937f5808b68c7eb39706f4fb755cbe9f3457824b7e09f206343ad79fef5039fbf967d42731bbed60d9125b7dd90c82d1a94e5244ffd0c7f16637c90506c0b6249527001d06e78ce4c5b355476e5dda67"
HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}

# ================= TASARIM =================
st.set_page_config(page_title="Motorcu Gezi Rehberi", page_icon="🏍️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
    html, body, [class*="css"] { font-family: 'Montserrat', sans-serif !important; }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {background-color: transparent !important;}
    
    .stApp { background-color: #0b0f19; color: #ffffff; }
    
    /* YAN MENÜ TASARIMI */
    [data-testid="stSidebar"] { background-color: #111520; border-right: 1px solid #1f2937; }
    
    /* HEADER VE BANNER TASARIMLARI */
    .hero-banner { background: linear-gradient(rgba(11, 15, 25, 0.6), rgba(11, 15, 25, 0.9)), url('https://images.unsplash.com/photo-1558981420-c532902e58b4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1920&q=80') center/cover; padding: 150px 20px; border-radius: 20px; text-align: center; border: 1px solid #2a2a4a; box-shadow: 0px 10px 30px rgba(0,0,0,0.5); margin-bottom: 2rem; margin-top: -50px; }
    .hero-title { background: -webkit-linear-gradient(45deg, #ff4b4b 0%, #ff904f 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 4.5rem; font-weight: 800; margin: 0; text-transform: uppercase; letter-spacing: 3px; }
    .hero-subtitle { color: #e2e8f0; font-size: 1.6rem; margin-top: 15px; font-weight: 600; text-shadow: 2px 2px 4px rgba(0,0,0,0.8); }
    
    .rota-bilgi-kutu { background: rgba(255, 255, 255, 0.05); padding: 25px; border-radius: 15px; border-left: 6px solid #ff4b4b; margin-bottom: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .rota-baslik { font-size: 1.8rem; font-weight: 800; color: #ff4b4b; margin-top: 0; margin-bottom: 10px; }
    .rota-detay { color: #cbd5e0; font-size: 1.1rem; line-height: 1.6; margin-bottom: 0; }
    
    /* KART TASARIMLARI */
    .place-card { display: flex; background-color: #111520; border-radius: 15px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.4); border: 1px solid #1f2937; margin-bottom: 30px; transition: transform 0.3s ease; }
    .place-card:hover { transform: translateY(-5px); border-color: #ff4b4b; box-shadow: 0 10px 25px rgba(255, 75, 75, 0.15); }
    .place-image-container { width: 45%; }
    .place-image { width: 100%; height: 100%; min-height: 300px; object-fit: cover; border-right: 3px solid #ff4b4b; display: block; }
    .place-content { width: 55%; padding: 30px; display: flex; flex-direction: column; justify-content: center; }
    .place-title { color: #ffffff; font-size: 2rem; font-weight: 800; margin-bottom: 15px; }
    .badge { background: #2d3748; color: #cbd5e0; padding: 6px 12px; border-radius: 8px; font-size: 0.9rem; font-weight: 600; display: inline-block; margin-right: 10px; border: 1px solid #4a5568; margin-bottom: 15px; }
    .badge-highlight { background: rgba(255, 75, 75, 0.1); color: #ff4b4b; border-color: #ff4b4b; }
    .badge-green { background: rgba(72, 187, 120, 0.1); color: #48bb78; border-color: #48bb78; }
    .desc-text { color: #a0aec0; font-size: 1.15rem; line-height: 1.7; }
    
    /* FOOTER (En Alt Kısım) */
    .custom-footer { background-color: #0b0f19; border-top: 1px solid #1f2937; padding: 30px; text-align: center; color: #718096; margin-top: 20px; font-size: 0.9rem; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# ================= YAN MENÜ =================
st.sidebar.markdown("<h2 style='text-align: center; color: #ff4b4b;'>Menü</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<br>", unsafe_allow_html=True)

sayfa = st.sidebar.radio("Menü", ["🏠 Ana Sayfa", "🗺️ Rotaları Keşfet"])

# ================= ANA SAYFA =================
if sayfa == "🏠 Ana Sayfa":
    st.markdown("""
        <div class="hero-banner">
            <h1 class="hero-title">Rüzgarı Hisset, Yolu Yaşa</h1>
            <p class="hero-subtitle">İki teker üzerinde dünyanın en nefes kesici rotalarını keşfetmek için doğru yerdesin.</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='min-height: 40vh;'></div>", unsafe_allow_html=True)

# ================= ROTALAR =================
elif sayfa == "🗺️ Rotaları Keşfet":
    st.markdown("<h1 style='color: #ff4b4b; text-transform: uppercase; letter-spacing: 2px;'>🗺️ Keşfe Çık</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #a0aec0; font-size: 1.1rem; margin-bottom: 30px;'>Gitmek istediğiniz rotayı seçin ve yapay zekanın size en iyi durakları sunmasına izin verin.</p>", unsafe_allow_html=True)
    
    @st.cache_data
    def rotalari_getir():
        try:
            req = requests.get(f"{STRAPI_URL}/api/cities?pagination[limit]=1000", headers=HEADERS)
            rotalar = [c.get('Ad', c.get('attributes', {}).get('Ad')) for c in req.json().get('data', []) if c]
            return ["🌍 Lütfen Bir Rota Seçin..."] + list(set(rotalar))
        except: return ["🌍 Lütfen Bir Rota Seçin..."]

    secilen_rota = st.selectbox("📍 Hedefinizi Belirleyin:", rotalari_getir())
    st.markdown("<br>", unsafe_allow_html=True)

    if secilen_rota != "🌍 Lütfen Bir Rota Seçin...":
        sehir_bilgileri = {
            "Antalya": "Akdeniz'in en güzel virajlarına sahip, manzarasıyla büyüleyen efsanevi sahil rotası. Bol virajlı ve genelde iyi asfaltlı yollarda dikkatli sürüş gerektirir.",
            "İzmir": "Tarihi taş evler, yel değirmenleri ve Ege'nin ılık rüzgarı eşliğinde keyifli bir sürüş. Çok iyi asfalt ve geniş yollar sizi bekliyor.",
            "Ege": "Tarihi taş evler, yel değirmenleri ve Ege'nin ılık rüzgarı eşliğinde keyifli bir sürüş. Çok iyi asfalt ve geniş yollar sizi bekliyor.",
            "Trans": "Dünyanın en iyi sürüş rotalarından biri kabul edilen, virajlarıyla baş döndüren efsanevi Transfăgărășan Geçidi. Yüksek rakımlı ve keskin virajlı dağ yolu.",
            "Karadeniz": "Yeşilin her tonunu görebileceğin, denizi bir yanda dağları diğer yanda bırakan oksijen dolu rota. Yaylalarda hafif toprak ve mıcır yollara dikkat.",
            "Route 66": "Amerika'nın ana caddesi, chopper motorların anavatanı. Uçsuz bucaksız çöl asfaltında özgürlüğü hissedeceğiniz efsanevi bir yolculuk.",
            "Amalfi": "Limon ağaçları ve sarp kayalıklar arasında İtalyan rüyası. Çok dar, uçurumlu ama bir o kadar da romantik Akdeniz yolları."
        }
        
        secilen_bilgi = "Motosikletinizle unutulmaz anılar biriktirebileceğiniz, manzarasıyla büyüleyen harika bir sürüş rotası."
        for anahtar, bilgi in sehir_bilgileri.items():
            if anahtar.lower() in secilen_rota.lower():
                secilen_bilgi = bilgi
                break
                
        st.markdown(f"""
            <div class="rota-bilgi-kutu">
                <h3 class="rota-baslik">📍 Rota Analizi: {secilen_rota}</h3>
                <p class="rota-detay">{secilen_bilgi}</p>
            </div>
        """, unsafe_allow_html=True)

        req = requests.get(f"{STRAPI_URL}/api/places?populate=*&pagination[limit]=1000", headers=HEADERS)
        if req.status_code == 200:
            tum_mekanlar = req.json().get('data', [])
            gosterilecek_mekanlar = []
            
            rota_lower = secilen_rota.lower()
            for mekan in tum_mekanlar:
                ad_orijinal = str(mekan.get('MekanAdi', mekan.get('attributes', {}).get('MekanAdi', '')))
                ad = ad_orijinal.lower()
                
                if "antalya" in rota_lower or "kaş" in rota_lower or "kas" in rota_lower:
                    if "kaputas" in ad or "kaputaş" in ad or "kalkan" in ad: gosterilecek_mekanlar.append(mekan)
                elif "izmir" in rota_lower or "ege" in rota_lower:
                    if "urla" in ad or "alaçatı" in ad or "alacati" in ad or "çeşme" in ad or "cesme" in ad: gosterilecek_mekanlar.append(mekan)
                elif "trans" in rota_lower or "romanya" in rota_lower:
                    if "bâlea" in ad or "balea" in ad or "vidraru" in ad: gosterilecek_mekanlar.append(mekan)
                elif "karadeniz" in rota_lower:
                    if "sümela" in ad or "sumela" in ad or "uzungöl" in ad or "uzungol" in ad: gosterilecek_mekanlar.append(mekan)
                elif "route 66" in rota_lower:
                    if "cadillac" in ad or "grand canyon" in ad: gosterilecek_mekanlar.append(mekan)
                elif "amalfi" in rota_lower or "italya" in rota_lower:
                    if "positano" in ad or "ravello" in ad: gosterilecek_mekanlar.append(mekan)

            if len(gosterilecek_mekanlar) == 0:
                st.warning("📍 Bu rotaya ait duraklar şu anda sisteme ekleniyor veya Strapi'de 'Taslak' modunda unutulmuş olabilir.")
            else:
                for mekan in gosterilecek_mekanlar:
                    ad = mekan.get('MekanAdi', mekan.get('attributes', {}).get('MekanAdi', 'Bilinmiyor'))
                    aciklama = mekan.get('Aciklama', mekan.get('attributes', {}).get('Aciklama')) or "Efsanevi manzaralar eşliğinde harika bir durak."
                    puan = mekan.get('Puan', mekan.get('attributes', {}).get('Puan', 4.8))
                    park = mekan.get('GuvenliPark', mekan.get('attributes', {}).get('GuvenliPark', True))
                    
                    resim_url = "https://images.unsplash.com/photo-1558981403-c5f9899a28bc"
                    try:
                        res_data = mekan.get('KapakResmi', mekan.get('attributes', {}).get('KapakResmi', {}))
                        if type(res_data) is dict and res_data.get('url'): resim_url = f"{STRAPI_URL}{res_data['url']}"
                    except: pass

                    kart_html = f'''
                    <div class="place-card">
                        <div class="place-image-container">
                            <img src="{resim_url}" class="place-image" alt="Mekan Görseli">
                        </div>
                        <div class="place-content">
                            <div class="place-title">{ad}</div>
                            <div class="badge-container">
                                <span class="badge badge-highlight">⭐ {puan} / 5.0 Puan</span>
                                <span class="badge {'badge-green' if park else ''}">🏍️ {'Güvenli Motor Parkı Var' if park else 'Park Alanı Yok'}</span>
                            </div>
                            <div class="desc-text">{aciklama}</div>
                        </div>
                    </div>
                    '''
                    st.markdown(kart_html, unsafe_allow_html=True)

# ================= FOOTER =================
st.markdown("""
    <div class="custom-footer">
        Gezi Rehberi Projesi
    </div>
""", unsafe_allow_html=True)