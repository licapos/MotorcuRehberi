import os
import requests
import urllib.parse
from deep_translator import GoogleTranslator

# ================= AYARLAR =================
STRAPI_URL = "https://motorcu-backend.onrender.com"
STRAPI_TOKEN = "380eacf98c36228e1228a7fced344573fbbd5c2c58208c943702073c000230b765e64ac9928da5e6c19a05c8a23c298f684e457a55fb6651c247fa9371266debf23a75d2d2b208e8d10d68b280d5e534efe8ebab2845b56f8028f2e5f23040fd230c91c40334000ffd536597a67ef9b0885d386d6e852cb1a0ee910bd58e037a"
HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}"}

# ================= DEVASA VERİ KÜMESİ =================
rotalar = [
    {
        "Ad": "Antalya - Kaş Sahil Yolu", "Ulke": "Türkiye",
        "KisaBilgi": "Akdeniz'in virajlı ve büyüleyici sahil rotası.", "YolDurumu": "İyi asfalt, bol viraj",
        "mekanlar": [
            {"MekanAdi": "Kaputaş Mola Noktası", "Aciklama": "Turkuaz suların muhteşem manzarası.", "Puan": 4.8, "GuvenliPark": True, "prompt": "Kaputas beach turquoise water cliff road"},
            {"MekanAdi": "Kalkan Seyir Tepesi", "Aciklama": "Güneşin batışını izlemek için efsanevi bir durak.", "Puan": 4.6, "GuvenliPark": False, "prompt": "Kalkan turkey sunset sea view high hill"}
        ]
    },
    {
        "Ad": "Ege: İzmir - Çeşme Rotası", "Ulke": "Türkiye",
        "KisaBilgi": "Tarihi taş evler ve Ege rüzgarı.", "YolDurumu": "Çok iyi asfalt",
        "mekanlar": [
            {"MekanAdi": "Urla İskelesi", "Aciklama": "Deniz kenarında yorgunluk kahvesi.", "Puan": 4.5, "GuvenliPark": True, "prompt": "Urla pier sea boats cloudy"},
            {"MekanAdi": "Alaçatı Yel Değirmenleri", "Aciklama": "Tarihi değirmenlerin gölgesinde fotoğraf molası.", "Puan": 4.7, "GuvenliPark": False, "prompt": "Alacati windmills stone traditional"},
            {"MekanAdi": "Çeşme Marina", "Aciklama": "Lüks yatların yanında güvenli motor parkı.", "Puan": 4.9, "GuvenliPark": True, "prompt": "Cesme marina luxury yachts sea"}
        ]
    },
    {
        "Ad": "Transfăgărășan Dağ Geçidi", "Ulke": "Romanya",
        "KisaBilgi": "Dünyanın en iyi sürüş rotalarından biri.", "YolDurumu": "Keskin virajlı dağ yolu",
        "mekanlar": [
            {"MekanAdi": "Bâlea Gölü Zirvesi", "Aciklama": "Bulutların üzerinde buz gibi dağ havası.", "Puan": 5.0, "GuvenliPark": True, "prompt": "Balea lake mountain peak clouds road"},
            {"MekanAdi": "Vidraru Barajı", "Aciklama": "Devasa baraj gövdesinin üzerinden geçiş.", "Puan": 4.6, "GuvenliPark": True, "prompt": "Vidraru dam deep valley concrete wall"}
        ]
    },
    {
        "Ad": "Amalfi Kıyıları", "Ulke": "İtalya",
        "KisaBilgi": "Limon ağaçları ve sarp kayalıklar arasında İtalyan rüyası.", "YolDurumu": "Çok dar ve uçurumlu",
        "mekanlar": [
            {"MekanAdi": "Positano Seyir Terası", "Aciklama": "Renkli evlerin denize döküldüğü o meşhur manzara.", "Puan": 4.9, "GuvenliPark": False, "prompt": "Positano italy colorful houses cliff sea"},
            {"MekanAdi": "Ravello Meydanı", "Aciklama": "Denizden yüksekte sessiz ve tarihi bir motor molası.", "Puan": 4.8, "GuvenliPark": True, "prompt": "Ravello square historic italy mountains"}
        ]
    },
    {
        "Ad": "Route 66", "Ulke": "ABD",
        "KisaBilgi": "Amerika'nın ana caddesi, chopper motorların anavatanı.", "YolDurumu": "Uçsuz bucaksız çöl asfaltı",
        "mekanlar": [
            {"MekanAdi": "Cadillac Ranch", "Aciklama": "Toprağa gömülü klasik arabaların olduğu sanat noktası.", "Puan": 4.5, "GuvenliPark": True, "prompt": "Cadillac ranch texas desert cars art"},
            {"MekanAdi": "Grand Canyon South Rim", "Aciklama": "Dünyanın en büyük kanyonuna karşı efsanevi bir durak.", "Puan": 5.0, "GuvenliPark": True, "prompt": "Grand canyon huge wide desert view"}
        ]
    }
]

# ================= 2. FONKSİYONLAR =================
def gorsel_uret(prompt, dosya_adi):
    print(f"[*] Görsel üretiliyor (Panoramik): {dosya_adi}...")
    safe_seed = urllib.parse.quote(prompt[:20])
    # DİKKAT: Resim boyutunu kartın kutusuna tam oturması için 1200x500 (Geniş/Panoramik) yaptık!
    url = f"https://picsum.photos/seed/{safe_seed}/1200/500"
    res = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if res.status_code == 200:
        with open(dosya_adi, 'wb') as f: f.write(res.content)
        return True
    return False

def strapi_yukle(dosya_adi):
    url = f"{STRAPI_URL}/api/upload"
    with open(dosya_adi, 'rb') as f:
        res = requests.post(url, headers=HEADERS, files={'files': (dosya_adi, f, 'image/jpeg')})
    if res.status_code in [200, 201]:
        return res.json()[0].get('id')
    return None

def otomasyon_baslat():
    for rota in rotalar:
        print(f"\n>>> Şehir: {rota['Ad']}")
        c_req = requests.post(f"{STRAPI_URL}/api/cities", headers=HEADERS, json={"data": {"Ad": rota["Ad"]}})
        
        if c_req.status_code == 201:
            for mekan in rota["mekanlar"]:
                dosya_adi = f"img_{mekan['prompt'][:10].replace(' ', '')}.jpg"
                if gorsel_uret(mekan["prompt"], dosya_adi):
                    img_id = strapi_yukle(dosya_adi)
                    if img_id:
                        # HACKER YÖNTEMİ: Şehrin adını HTML damgası olarak açıklamanın sonuna gizliyoruz!
                        gizli_damga = f" <span style='display:none;'>{rota['Ad']}</span>"
                        p_data = {
                            "data": {
                                "MekanAdi": mekan["MekanAdi"],
                                "Aciklama": mekan["Aciklama"] + gizli_damga,
                                "Puan": mekan["Puan"],
                                "GuvenliPark": mekan["GuvenliPark"],
                                "KapakResmi": img_id
                            }
                        }
                        requests.post(f"{STRAPI_URL}/api/places", headers=HEADERS, json=p_data)
                if os.path.exists(dosya_adi): os.remove(dosya_adi)

if __name__ == "__main__":
    otomasyon_baslat()
    print("--- Tüm Dünyadaki Rotalar Eklendi ---")