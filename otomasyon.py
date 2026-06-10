import requests
# 1. AYARLAR - Burayı kendi bilgilerinle güncelle
# ÖNEMLİ: URL'yi kendi Render backend adresinle eşleştir
STRAPI_URL = "https://motorcu-api.onrender.com"
API_TOKEN = "5aa3724f06753541c0f53f014b65cb32060d92be8df3aae761e3a8698677b6e3e077b92f5cb677e7b76e6f88a9627fec4c21caa6d7182006f2ada223e3741600fa115358bd28040d104b4397c851e169bd79d338029ff62f936d97cf93d4f976061114cefd3a5f327fcf3990cba2efee2454d9cec628d53822adca13d932e480" 
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
