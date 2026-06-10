import requests
# 1. AYARLAR - Burayı kendi bilgilerinle güncelle
# ÖNEMLİ: URL'yi kendi Render backend adresinle eşleştir
STRAPI_URL = "https://motorcu-api.onrender.com"
API_TOKEN = "41506ef41506efe63774ce97ca51606fe08f903d36090939a982c42e4080f07797c07fad7720f669888121c4090ac67fbd3f4e99cf4cc097555b42b703a9ce7587bcb80df2f019a01757bfccfac9cad804054f7819a950122451ab91cf1ff8d7c8f4af8f77c90618ea613e89f81171b61fb2d1c99d490415f38c5d16c14afc72ba90fcbe63774ce97ca51606fe08f903d36090939a982c42e4080f07797c07fad7720f669888121c4090ac67fbd3f4e99cf4cc097555b42b703a9ce7587bcb80df2f019a01757bfccfac9cad804054f7819a950122451ab91cf1ff8d7c8f4af8f77c90618ea613e89f81171b61fb2d1c99d490415f38c5d16c14afc72ba90fcb" 
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
