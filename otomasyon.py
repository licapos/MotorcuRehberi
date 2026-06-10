"""
Motorcu Gezi Rehberi — Otomasyon Motoru
========================================
Bu script çalıştırıldığında:
1. Hazır veri listesinden mekân bilgilerini alır
2. deep-translator ile Türkçe açıklamaları İngilizceye çevirir
3. Hugging Face API ile mekâna uygun turistik/manzara görseli üretir
4. Görseli Strapi Media Library'ye yükler
5. TR ve EN olarak Strapi API'ye kaydeder
"""

import requests
import time
import os
from deep_translator import GoogleTranslator

# ======================== AYARLAR ========================
STRAPI_URL = "https://motorcu-api.onrender.com"

# Strapi API Token — Admin panelinden oluşturduğun token'ı buraya yapıştır
STRAPI_API_TOKEN = "BURAYA_STRAPI_TOKEN_YAPISTIR"

# Hugging Face API Token — https://huggingface.co/settings/tokens adresinden al
HF_API_TOKEN = "BURAYA_HUGGINGFACE_TOKEN_YAPISTIR"

# Hugging Face görsel üretim modeli
HF_MODEL = "stabilityai/stable-diffusion-xl-base-1.0"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL}"

HEADERS = {
    "Authorization": f"Bearer {STRAPI_API_TOKEN}",
    "Content-Type": "application/json"
}
# =========================================================

# ======================== VERİ LİSTESİ ========================
# Her şehir için mekân bilgileri (Türkçe)
SEHIR_MEKANLARI = {
    "Antalya - Kaş Sahil Yolu": {
        "ulke": "Türkiye",
        "kisa_bilgi": "Akdeniz'in turkuaz kıyıları boyunca uzanan, motosiklet tutkunlarının vazgeçilmez rotası.",
        "mekanlar": [
            {
                "MekanAdi": "Olimpos Antik Kenti",
                "Aciklama": "Likya uygarlığına ait bu antik kent, çam ormanları arasında denize sıfır konumuyla büyüleyici bir atmosfer sunar. Yanartaş (Chimaera) doğal alevleri de yakınındadır.",
                "Puan": 4.7
            },
            {
                "MekanAdi": "Kaş Marina",
                "Aciklama": "Akdeniz'in en berrak sularına sahip bu küçük liman kasabası, dalış sporları, tekne turları ve romantik sokak kafeleriyle ünlüdür.",
                "Puan": 4.5
            },
            {
                "MekanAdi": "Demre Myra Antik Kenti",
                "Aciklama": "Noel Baba'nın yaşadığı yer olarak bilinen Demre'deki Myra, kayalara oyulmuş muhteşem Likya kaya mezarlarıyla ziyaretçilerini büyüler.",
                "Puan": 4.6
            }
        ]
    },
    "Route 66": {
        "ulke": "ABD",
        "kisa_bilgi": "Chicago'dan Los Angeles'a uzanan efsanevi Amerikan yolu, motosiklet kültürünün simgesi.",
        "mekanlar": [
            {
                "MekanAdi": "Grand Canyon",
                "Aciklama": "Dünyanın en büyük ve en etkileyici kanyonu olan Grand Canyon, milyonlarca yıllık doğal erozyonun yarattığı muhteşem bir doğa harikasıdır.",
                "Puan": 4.9
            },
            {
                "MekanAdi": "Cadillac Ranch",
                "Aciklama": "Teksas çölünde toprağa gömülmüş 10 adet Cadillac otomobilin oluşturduğu bu sanat eseri, Route 66'nın en ikonik duraklarından biridir.",
                "Puan": 4.2
            },
            {
                "MekanAdi": "Santa Monica Pier",
                "Aciklama": "Route 66'nın batı ucundaki son durak olan Santa Monica İskelesi, Pasifik Okyanusu manzarası, lunapark ve sokak sanatçılarıyla ünlüdür.",
                "Puan": 4.4
            }
        ]
    }
}
# ==============================================================


def cevir_ingilizce(metin):
    """Türkçe metni İngilizceye çevirir (deep-translator)"""
    try:
        sonuc = GoogleTranslator(source='tr', target='en').translate(metin)
        print(f"   ✅ Çeviri başarılı")
        return sonuc
    except Exception as e:
        print(f"   ⚠️ Çeviri hatası: {e}")
        return metin  # Hata olursa orijinali döndür


def gorsel_uret(mekan_adi, sehir_adi):
    """Hugging Face API ile mekâna uygun turistik görsel üretir"""
    prompt = f"Beautiful tourist photograph of {mekan_adi}, {sehir_adi}, scenic landscape, professional travel photography, golden hour lighting, high resolution, 4k"

    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    print(f"   🎨 Görsel üretiliyor: {mekan_adi}...")

    try:
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json={"inputs": prompt},
            timeout=120
        )

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            if "image" in content_type:
                print(f"   ✅ Görsel üretildi ({len(response.content)} bytes)")
                return response.content
            else:
                print(f"   ⚠️ Beklenmeyen yanıt tipi: {content_type}")
                return None
        elif response.status_code == 503:
            # Model yükleniyor, bekle ve tekrar dene
            print(f"   ⏳ Model yükleniyor, 30 saniye bekleniyor...")
            time.sleep(30)
            response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt}, timeout=120)
            if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                print(f"   ✅ Görsel üretildi (2. deneme)")
                return response.content
            else:
                print(f"   ❌ 2. deneme de başarısız (Kod: {response.status_code})")
                return None
        else:
            print(f"   ❌ Görsel üretilemedi (Kod: {response.status_code}): {response.text[:200]}")
            return None
    except requests.exceptions.Timeout:
        print(f"   ❌ Görsel üretme zaman aşımına uğradı")
        return None
    except Exception as e:
        print(f"   ❌ Görsel hatası: {e}")
        return None


def strapi_gorsel_yukle(gorsel_bytes, dosya_adi):
    """Görseli Strapi Media Library'ye yükler, media ID döner"""
    upload_url = f"{STRAPI_URL}/api/upload"
    auth_headers = {"Authorization": f"Bearer {STRAPI_API_TOKEN}"}

    files = {
        "files": (dosya_adi, gorsel_bytes, "image/png")
    }

    try:
        response = requests.post(upload_url, headers=auth_headers, files=files, timeout=60)
        if response.status_code == 200 or response.status_code == 201:
            media_data = response.json()
            if isinstance(media_data, list) and len(media_data) > 0:
                media_id = media_data[0]["id"]
                print(f"   ✅ Görsel Strapi'ye yüklendi (Media ID: {media_id})")
                return media_id
        print(f"   ❌ Görsel yükleme hatası (Kod: {response.status_code}): {response.text[:200]}")
        return None
    except Exception as e:
        print(f"   ❌ Görsel yükleme hatası: {e}")
        return None


def sehir_bul_veya_olustur(sehir_adi, ulke, kisa_bilgi):
    """Strapi'de şehri arar, yoksa oluşturur. documentId döner."""
    # Önce ara
    try:
        search_url = f"{STRAPI_URL}/api/cities?filters[Ad][$eq]={requests.utils.quote(sehir_adi)}&locale=en"
        response = requests.get(search_url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                doc_id = data[0].get("documentId")
                print(f"   📍 Şehir bulundu: {sehir_adi} (ID: {doc_id})")
                return doc_id
    except Exception:
        pass

    # Yoksa oluştur
    try:
        city_data = {
            "data": {
                "Ad": sehir_adi,
                "Ulke": ulke,
                "KisaBilgi": kisa_bilgi
            }
        }
        create_url = f"{STRAPI_URL}/api/cities"
        response = requests.post(create_url, headers=HEADERS, json=city_data)
        if response.status_code in [200, 201]:
            doc_id = response.json().get("data", {}).get("documentId")
            print(f"   ✅ Şehir oluşturuldu: {sehir_adi} (ID: {doc_id})")

            # Publish et
            publish_url = f"{STRAPI_URL}/api/cities/{doc_id}/actions/publish"
            requests.post(publish_url, headers=HEADERS, json={})

            return doc_id
        else:
            print(f"   ❌ Şehir oluşturma hatası: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   ❌ Şehir hatası: {e}")
        return None


def mekan_olustur(mekan, sehir_doc_id, sehir_adi, media_id, aciklama_en):
    """Strapi'de mekân kaydı oluşturur (TR locale)"""
    try:
        place_data = {
            "data": {
                "MekanAdi": mekan["MekanAdi"],
                "Aciklama": mekan["Aciklama"],
                "AciklamaEN": aciklama_en,
                "Puan": mekan["Puan"],
                "city": sehir_doc_id,
            }
        }

        # Görsel varsa ekle
        if media_id:
            place_data["data"]["KapakResmi"] = media_id

        create_url = f"{STRAPI_URL}/api/places"
        response = requests.post(create_url, headers=HEADERS, json=place_data)

        if response.status_code in [200, 201]:
            doc_id = response.json().get("data", {}).get("documentId")
            print(f"   ✅ Mekân oluşturuldu: {mekan['MekanAdi']} (ID: {doc_id})")

            # Publish et
            publish_url = f"{STRAPI_URL}/api/places/{doc_id}/actions/publish"
            requests.post(publish_url, headers=HEADERS, json={})
            print(f"   ✅ Mekân yayınlandı")

            return doc_id
        else:
            print(f"   ❌ Mekân oluşturma hatası (Kod: {response.status_code}): {response.text[:300]}")
            return None
    except Exception as e:
        print(f"   ❌ Mekân hatası: {e}")
        return None


def otomasyon_baslat():
    """Ana otomasyon döngüsü — tek tuşla çalışır"""
    print("=" * 60)
    print("🏍️  MOTORCU GEZİ REHBERİ — OTOMASYON MOTORU")
    print("=" * 60)
    print()

    toplam_mekan = sum(len(v["mekanlar"]) for v in SEHIR_MEKANLARI.values())
    print(f"📊 {len(SEHIR_MEKANLARI)} şehir, {toplam_mekan} mekân işlenecek")
    print()

    basarili = 0
    hatali = 0

    for sehir_adi, sehir_verisi in SEHIR_MEKANLARI.items():
        print(f"\n{'='*50}")
        print(f"🌍 ŞEHİR: {sehir_adi} ({sehir_verisi['ulke']})")
        print(f"{'='*50}")

        # 1. Şehri bul veya oluştur
        sehir_doc_id = sehir_bul_veya_olustur(
            sehir_adi,
            sehir_verisi["ulke"],
            sehir_verisi["kisa_bilgi"]
        )

        if not sehir_doc_id:
            print(f"   ❌ Şehir oluşturulamadı, mekânlar atlanıyor!")
            hatali += len(sehir_verisi["mekanlar"])
            continue

        # 2. Her mekân için işlem yap
        for i, mekan in enumerate(sehir_verisi["mekanlar"], 1):
            print(f"\n   --- Mekân {i}/{len(sehir_verisi['mekanlar'])}: {mekan['MekanAdi']} ---")

            # 2a. Çeviri (TR → EN)
            print(f"   🔄 Çeviri yapılıyor...")
            aciklama_en = cevir_ingilizce(mekan["Aciklama"])

            # 2b. AI Görsel Üretimi
            gorsel_bytes = gorsel_uret(mekan["MekanAdi"], sehir_adi)

            # 2c. Görseli Strapi Media Library'ye yükle
            media_id = None
            if gorsel_bytes:
                dosya_adi = f"{mekan['MekanAdi'].replace(' ', '_').lower()}.png"
                media_id = strapi_gorsel_yukle(gorsel_bytes, dosya_adi)

            # 2d. Mekânı Strapi'ye kaydet
            sonuc = mekan_olustur(mekan, sehir_doc_id, sehir_adi, media_id, aciklama_en)

            if sonuc:
                basarili += 1
            else:
                hatali += 1

            # Rate limiting - API'yi boğmamak için kısa bekleme
            time.sleep(2)

    # Sonuç raporu
    print(f"\n{'='*60}")
    print(f"📊 SONUÇ RAPORU")
    print(f"{'='*60}")
    print(f"   ✅ Başarılı: {basarili} mekân")
    print(f"   ❌ Hatalı:   {hatali} mekân")
    print(f"   📊 Toplam:   {basarili + hatali} mekân")
    print(f"{'='*60}")
    print(f"🏁 Otomasyon tamamlandı!")


if __name__ == "__main__":
    otomasyon_baslat()
