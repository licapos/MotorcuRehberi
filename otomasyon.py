# -*- coding: utf-8 -*-
"""
Motorcu Gezi Rehberi - Otomasyon Motoru
========================================
Bu script calistirildiginda:
1. Hazir veri listesinden mekan bilgilerini alir
2. deep-translator ile Turkce aciklamalari Ingilizceye cevirir
3. Hugging Face API ile mekana uygun turistik gorsel uretir
4. Gorseli Strapi Media Library'ye yukler
5. Strapi API'ye kaydeder
"""

import requests
import time
import sys
import io
from deep_translator import GoogleTranslator

# Windows konsol encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# ======================== AYARLAR ========================
STRAPI_URL = "https://motorcu-api.onrender.com"

import os
STRAPI_API_TOKEN = os.environ.get("STRAPI_TOKEN", "")

HF_API_TOKEN = os.environ.get("HF_TOKEN", "")
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

HEADERS = {
    "Authorization": f"Bearer {STRAPI_API_TOKEN}",
    "Content-Type": "application/json"
}
# =========================================================

# ======================== VERI LISTESI ========================
SEHIR_MEKANLARI = {
    "Antalya - Kas Sahil Yolu": {
        "ulke": "Turkiye",
        "kisa_bilgi": "Akdeniz'in turkuaz kiyilari boyunca uzanan, motosiklet tutkunlarinin vazgecilmez rotasi.",
        "mekanlar": [
            {
                "MekanAdi": "Olimpos Antik Kenti",
                "Aciklama": "Likya uygarligina ait bu antik kent, cam ormanlari arasinda denize sifir konumuyla buyuleyici bir atmosfer sunar. Yanartas (Chimaera) dogal alevleri de yakinindadir.",
                "Puan": 4.7
            },
            {
                "MekanAdi": "Kas Marina",
                "Aciklama": "Akdeniz'in en berrak sularina sahip bu kucuk liman kasabasi, dalis sporlari, tekne turlari ve romantik sokak kafeleriyle unludur.",
                "Puan": 4.5
            },
            {
                "MekanAdi": "Demre Myra Antik Kenti",
                "Aciklama": "Noel Baba'nin yasadigi yer olarak bilinen Demre'deki Myra, kayalara oyulmus muhtesem Likya kaya mezarlariyla ziyaretcilerini buyuler.",
                "Puan": 4.6
            }
        ]
    },
    "Route 66": {
        "ulke": "ABD",
        "kisa_bilgi": "Chicago'dan Los Angeles'a uzanan efsanevi Amerikan yolu, motosiklet kulturunun simgesi.",
        "mekanlar": [
            {
                "MekanAdi": "Grand Canyon",
                "Aciklama": "Dunyanin en buyuk ve en etkileyici kanyonu olan Grand Canyon, milyonlarca yillik dogal erozyonun yarattigi muhtesem bir doga harikasi.",
                "Puan": 4.9
            },
            {
                "MekanAdi": "Cadillac Ranch",
                "Aciklama": "Teksas colunde topraga gomulmus 10 adet Cadillac otomobilin olusturdugu bu sanat eseri, Route 66'nin en ikonik duraklarindan biridir.",
                "Puan": 4.2
            },
            {
                "MekanAdi": "Santa Monica Pier",
                "Aciklama": "Route 66'nin bati ucundaki son durak olan Santa Monica Iskelesi, Pasifik Okyanusu manzarasi, lunapark ve sokak sanatcilariyla unludur.",
                "Puan": 4.4
            }
        ]
    }
}
# ==============================================================


def cevir_ingilizce(metin):
    """Turkce metni Ingilizceye cevirir (deep-translator)"""
    try:
        sonuc = GoogleTranslator(source='tr', target='en').translate(metin)
        print(f"   [OK] Ceviri basarili")
        return sonuc
    except Exception as e:
        print(f"   [!] Ceviri hatasi: {e}")
        return metin


def gorsel_uret(mekan_adi, sehir_adi):
    """Hugging Face Inference API ile mekana uygun turistik gorsel uretir"""
    prompt = f"Beautiful tourist photograph of {mekan_adi}, {sehir_adi}, scenic landscape, travel photography, 4k"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}

    print(f"   [ART] Gorsel uretiliyor: {mekan_adi}...")

    max_deneme = 3
    for deneme in range(1, max_deneme + 1):
        try:
            response = requests.post(
                HF_API_URL,
                headers=headers,
                json={"inputs": prompt},
                timeout=180
            )

            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                if "image" in content_type:
                    print(f"   [OK] Gorsel uretildi ({len(response.content)} bytes)")
                    return response.content
                else:
                    print(f"   [!] Beklenmeyen yanit: {content_type}")
                    return None
            elif response.status_code == 503:
                wait = 30 * deneme
                print(f"   [WAIT] Model yukleniyor, {wait}sn bekleniyor... (deneme {deneme}/{max_deneme})")
                time.sleep(wait)
                continue
            else:
                print(f"   [X] Gorsel hatasi (Kod: {response.status_code}): {response.text[:150]}")
                return None
        except requests.exceptions.Timeout:
            print(f"   [X] Zaman asimi (deneme {deneme}/{max_deneme})")
            continue
        except Exception as e:
            print(f"   [X] Gorsel hatasi: {e}")
            return None

    print(f"   [X] {max_deneme} deneme sonrasi gorsel uretilemedi")
    return None


def strapi_gorsel_yukle(gorsel_bytes, dosya_adi):
    """Gorseli Strapi Media Library'ye yukler, media ID doner"""
    upload_url = f"{STRAPI_URL}/api/upload"
    auth_headers = {"Authorization": f"Bearer {STRAPI_API_TOKEN}"}
    files = {"files": (dosya_adi, gorsel_bytes, "image/png")}

    try:
        response = requests.post(upload_url, headers=auth_headers, files=files, timeout=60)
        if response.status_code in [200, 201]:
            media_data = response.json()
            if isinstance(media_data, list) and len(media_data) > 0:
                media_id = media_data[0]["id"]
                print(f"   [OK] Gorsel Strapi'ye yuklendi (Media ID: {media_id})")
                return media_id
        print(f"   [X] Gorsel yukleme hatasi (Kod: {response.status_code}): {response.text[:200]}")
        return None
    except Exception as e:
        print(f"   [X] Gorsel yukleme hatasi: {e}")
        return None


def sehir_bul_veya_olustur(sehir_adi, ulke, kisa_bilgi):
    """Strapi'de sehri arar, yoksa olusturur. documentId doner."""
    try:
        search_url = f"{STRAPI_URL}/api/cities?filters[Ad][$eq]={requests.utils.quote(sehir_adi)}&locale=en"
        response = requests.get(search_url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json().get("data", [])
            if data:
                doc_id = data[0].get("documentId")
                print(f"   [FOUND] Sehir bulundu: {sehir_adi} (ID: {doc_id})")
                return doc_id
    except Exception:
        pass

    try:
        city_data = {"data": {"Ad": sehir_adi, "Ulke": ulke, "KisaBilgi": kisa_bilgi}}
        response = requests.post(f"{STRAPI_URL}/api/cities", headers=HEADERS, json=city_data)
        if response.status_code in [200, 201]:
            doc_id = response.json().get("data", {}).get("documentId")
            print(f"   [OK] Sehir olusturuldu: {sehir_adi} (ID: {doc_id})")
            requests.post(f"{STRAPI_URL}/api/cities/{doc_id}/actions/publish", headers=HEADERS, json={})
            return doc_id
        else:
            print(f"   [X] Sehir hatasi: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"   [X] Sehir hatasi: {e}")
        return None


def mekan_olustur(mekan, sehir_doc_id, media_id, aciklama_en):
    """Strapi'de mekan kaydi olusturur"""
    try:
        aciklama_birlesik = f"{mekan['Aciklama']}\n\n[EN] {aciklama_en}"

        place_data = {
            "data": {
                "MekanAdi": mekan["MekanAdi"],
                "Aciklama": aciklama_birlesik,
                "Puan": mekan["Puan"],
            }
        }

        # city iliskisi varsa ekle, yoksa atla
        try:
            test = requests.post(
                f"{STRAPI_URL}/api/places",
                headers=HEADERS,
                json={"data": {"MekanAdi": "_test_", "city": sehir_doc_id}},
                timeout=10
            )
            if test.status_code in [200, 201]:
                # city calisiyor, test kaydini sil
                test_doc = test.json().get("data", {}).get("documentId")
                if test_doc:
                    requests.delete(f"{STRAPI_URL}/api/places/{test_doc}", headers=HEADERS)
                place_data["data"]["city"] = sehir_doc_id
            # 400 donerse city alani yok, ekleme
        except Exception:
            pass

        if media_id:
            place_data["data"]["KapakResmi"] = media_id

        response = requests.post(f"{STRAPI_URL}/api/places", headers=HEADERS, json=place_data)

        if response.status_code in [200, 201]:
            doc_id = response.json().get("data", {}).get("documentId")
            print(f"   [OK] Mekan olusturuldu: {mekan['MekanAdi']} (ID: {doc_id})")
            requests.post(f"{STRAPI_URL}/api/places/{doc_id}/actions/publish", headers=HEADERS, json={})
            print(f"   [OK] Mekan yayinlandi")
            return doc_id
        else:
            print(f"   [X] Mekan hatasi (Kod: {response.status_code}): {response.text[:300]}")
            return None
    except Exception as e:
        print(f"   [X] Mekan hatasi: {e}")
        return None


def otomasyon_baslat():
    """Ana otomasyon dongusu - tek tusla calisir"""
    print("=" * 60)
    print("MOTORCU GEZI REHBERI - OTOMASYON MOTORU")
    print("=" * 60)

    toplam = sum(len(v["mekanlar"]) for v in SEHIR_MEKANLARI.values())
    print(f">> {len(SEHIR_MEKANLARI)} sehir, {toplam} mekan islenecek\n")

    basarili = 0
    hatali = 0

    for sehir_adi, sv in SEHIR_MEKANLARI.items():
        print(f"\n{'='*50}")
        print(f"SEHIR: {sehir_adi} ({sv['ulke']})")
        print(f"{'='*50}")

        sehir_doc_id = sehir_bul_veya_olustur(sehir_adi, sv["ulke"], sv["kisa_bilgi"])
        if not sehir_doc_id:
            hatali += len(sv["mekanlar"])
            continue

        for i, mekan in enumerate(sv["mekanlar"], 1):
            print(f"\n   --- Mekan {i}/{len(sv['mekanlar'])}: {mekan['MekanAdi']} ---")

            print(f"   [TR->EN] Ceviri yapiliyor...")
            aciklama_en = cevir_ingilizce(mekan["Aciklama"])

            gorsel_bytes = gorsel_uret(mekan["MekanAdi"], sehir_adi)

            media_id = None
            if gorsel_bytes:
                dosya_adi = f"{mekan['MekanAdi'].replace(' ', '_').lower()}.png"
                media_id = strapi_gorsel_yukle(gorsel_bytes, dosya_adi)

            sonuc = mekan_olustur(mekan, sehir_doc_id, media_id, aciklama_en)
            if sonuc:
                basarili += 1
            else:
                hatali += 1

            time.sleep(2)

    print(f"\n{'='*60}")
    print(f"SONUC RAPORU")
    print(f"{'='*60}")
    print(f"   Basarili: {basarili} mekan")
    print(f"   Hatali:   {hatali} mekan")
    print(f"   Toplam:   {basarili + hatali} mekan")
    print(f"{'='*60}")


if __name__ == "__main__":
    otomasyon_baslat()
