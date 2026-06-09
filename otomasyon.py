import requests

# 1. AYARLAR - Burayı kendi bilgilerinle güncelle
STRAPI_URL = "https://motorcu-backend.onrender.com"
API_TOKEN = "380eacf98c36228e1228a7fced344573fbbd5c2c58208c943702073c000230b765e64ac9928da5e6c19a05c8a23c298f684e457a55fb6651c247fa9371266debf23a75d2d2b208e8d10d68b280d5e534efe8ebab2845b56f8028f2e5f23040fd230c91c40334000ffd536597a67ef9b0885d386d6e852cb1a0ee910bd58e037a" 

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