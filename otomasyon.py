import requests

# 1. AYARLAR - Burayı kendi bilgilerinle güncelle
STRAPI_URL = "https://motorcu-backend.onrender.com"
API_TOKEN = "86fe39d30c1c14bcddc8cf8dab542de329da9539f2439767380e9a4201d9a2998796e76495de80e630ffc6601adff09d494012e27210ddc48703a49406270b1344543058721d0336b568ac8934ca2c83d8f1f8d513b7eb32c3e32313a8a935908af98aeb745f78e45fcdceec9d17853b342e96fa2800f915bb80e72ce885f4ce" 

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def otomasyon_baslat():
    # Rotaların
    rotalar = [
        {"Ad": "Antalya - Kaş Sahil Yolu"},
        {"Ad": "Route 66"}
    ]

    print(f"--- Bağlantı kuruluyor: {STRAPI_URL} ---")

    for rota in rotalar:
        try:
            print(f">>> Ekleniyor: {rota['Ad']}")
            
            # POST işlemi
            c_req = requests.post(
                f"{STRAPI_URL}/api/cities", 
                headers=HEADERS, 
                json={"data": {"Ad": rota["Ad"]}}
            )
            
            # Sonucu yazdır (Hata çıkarsa buradan göreceğiz)
            print(f"Status Kodu: {c_req.status_code}")
            if c_req.status_code >= 200 and c_req.status_code < 300:
                print("Sonuç: BAŞARILI!")
            else:
                print(f"Sonuç: HATA! Detay: {c_req.text}")
                
        except Exception as e:
            print(f"Beklenmedik bir hata oluştu: {e}")
        
        print("-" * 40)

    print("--- Tüm Rotalar İşlendi ---")

if __name__ == "__main__":
    otomasyon_baslat()