# -*- coding: utf-8 -*-
# otomasyon scripti
# sehir ve mekan bilgilerini strapi'ye yukler
# ceviri icin deep-translator, gorsel icin hugging face kullaniyorum

import requests
import time
import sys
import io
import os
from deep_translator import GoogleTranslator

# windows'ta turkce karakter sorunu icin
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# api adresleri ve tokenlar
STRAPI_URL = "https://motorcu-api.onrender.com"
STRAPI_API_TOKEN = os.environ.get("STRAPI_TOKEN", "")
HF_API_TOKEN = os.environ.get("HF_TOKEN", "")
HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

HEADERS = {
    "Authorization": f"Bearer {STRAPI_API_TOKEN}",
    "Content-Type": "application/json"
}

# mekan verileri - her sehir icin ayri ayri tanimladim
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


# turkce metni ingilizceye cevirir
def cevir_ingilizce(metin):
    try:
        sonuc = GoogleTranslator(source='tr', target='en').translate(metin)
        print(f"   [OK] Ceviri basarili")
        return sonuc
    except Exception as e:
        print(f"   [!] Ceviri hatasi: {e}")
        return metin


# hugging face uzerinden gorsel uretir
def gorsel_uret(mekan_adi, sehir_adi):
    prompt = f"Beautiful tourist photograph of {mekan_adi}, {sehir_adi}, scenic landscape, travel photography, 4k"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    print(f"   [ART] Gorsel uretiliyor: {mekan_adi}...")

    # 3 kere deniyor, bazen model yuklenmesi gerekiyor
    for deneme in range(1, 4):
        try:
            response = requests.post(HF_API_URL, headers=headers, json={"inputs": prompt}, timeout=180)
            if response.status_code == 200 and "image" in response.headers.get("content-type", ""):
                print(f"   [OK] Gorsel uretildi ({len(response.content)} bytes)")
                return response.content
            elif response.status_code == 503:
                print(f"   [WAIT] Model yukleniyor, bekliyorum... ({deneme}/3)")
                time.sleep(30 * deneme)
                continue
            else:
                print(f"   [X] Gorsel hatasi (Kod: {response.status_code})")
                return None
        except:
            print(f"   [X] Baglanti hatasi (deneme {deneme}/3)")
            continue
    return None


# gorseli strapi media library'ye yukler
def strapi_gorsel_yukle(gorsel_bytes, dosya_adi):
    files = {"files": (dosya_adi, gorsel_bytes, "image/png")}
    auth = {"Authorization": f"Bearer {STRAPI_API_TOKEN}"}
    try:
        r = requests.post(f"{STRAPI_URL}/api/upload", headers=auth, files=files, timeout=60)
        if r.status_code in [200, 201]:
            media_id = r.json()[0]["id"]
            print(f"   [OK] Gorsel yuklendi (ID: {media_id})")
            return media_id
        print(f"   [X] Yukleme hatasi: {r.status_code}")
    except Exception as e:
        print(f"   [X] Yukleme hatasi: {e}")
    return None


# strapi'de sehri arar yoksa olusturur
def sehir_bul_veya_olustur(sehir_adi, ulke, kisa_bilgi):
    # once var mi bak
    try:
        r = requests.get(f"{STRAPI_URL}/api/cities?filters[Ad][$eq]={requests.utils.quote(sehir_adi)}&locale=tr", headers=HEADERS)
        data = r.json().get("data", [])
        if data:
            doc_id = data[0].get("documentId")
            print(f"   [FOUND] {sehir_adi} zaten var (ID: {doc_id})")
            return doc_id
    except:
        pass

    # yoksa olustur
    try:
        r = requests.post(f"{STRAPI_URL}/api/cities", headers=HEADERS, json={"data": {"Ad": sehir_adi, "Ulke": ulke, "KisaBilgi": kisa_bilgi}})
        if r.status_code in [200, 201]:
            doc_id = r.json()["data"]["documentId"]
            print(f"   [OK] {sehir_adi} olusturuldu (ID: {doc_id})")
            requests.post(f"{STRAPI_URL}/api/cities/{doc_id}/actions/publish", headers=HEADERS, json={})
            return doc_id
    except Exception as e:
        print(f"   [X] Sehir hatasi: {e}")
    return None


# mekani strapi'ye kaydeder
def mekan_olustur(mekan, sehir_doc_id, media_id, aciklama_en):
    try:
        # turkce ve ingilizce aciklamayi birlestirdim
        aciklama = f"{mekan['Aciklama']}\n\n[EN] {aciklama_en}"
        data = {"data": {"MekanAdi": mekan["MekanAdi"], "Aciklama": aciklama, "Puan": mekan["Puan"]}}
        if media_id:
            data["data"]["KapakResmi"] = media_id

        r = requests.post(f"{STRAPI_URL}/api/places", headers=HEADERS, json=data)
        if r.status_code in [200, 201]:
            doc_id = r.json()["data"]["documentId"]
            print(f"   [OK] {mekan['MekanAdi']} olusturuldu")
            requests.post(f"{STRAPI_URL}/api/places/{doc_id}/actions/publish", headers=HEADERS, json={})
            return doc_id
        else:
            print(f"   [X] Hata ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"   [X] Mekan hatasi: {e}")
    return None


# ana fonksiyon - her seyi sirayla yapar
def calistir():
    print("=" * 50)
    print("MOTORCU GEZI REHBERI - OTOMASYON")
    print("=" * 50)

    toplam = sum(len(v["mekanlar"]) for v in SEHIR_MEKANLARI.values())
    print(f"\n{len(SEHIR_MEKANLARI)} sehir, {toplam} mekan islenecek\n")

    basarili = 0

    for sehir_adi, sv in SEHIR_MEKANLARI.items():
        print(f"\n--- {sehir_adi} ({sv['ulke']}) ---")

        sehir_id = sehir_bul_veya_olustur(sehir_adi, sv["ulke"], sv["kisa_bilgi"])
        if not sehir_id:
            continue

        for i, mekan in enumerate(sv["mekanlar"], 1):
            print(f"\n   Mekan {i}/{len(sv['mekanlar'])}: {mekan['MekanAdi']}")

            # 1) ceviri yap
            en_text = cevir_ingilizce(mekan["Aciklama"])

            # 2) gorsel uret
            gorsel = gorsel_uret(mekan["MekanAdi"], sehir_adi)

            # 3) gorseli yukle
            media_id = None
            if gorsel:
                media_id = strapi_gorsel_yukle(gorsel, f"{mekan['MekanAdi'].replace(' ','_').lower()}.png")

            # 4) mekani kaydet
            if mekan_olustur(mekan, sehir_id, media_id, en_text):
                basarili += 1

            time.sleep(2)

    print(f"\n{'='*50}")
    print(f"Bitti! {basarili}/{toplam} mekan basariyla eklendi.")


if __name__ == "__main__":
    calistir()
