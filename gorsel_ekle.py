# -*- coding: utf-8 -*-
"""Mevcut mekanlara AI gorsel ekler"""
import requests, time, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

STRAPI_URL = "https://motorcu-api.onrender.com"
import os
STRAPI_TOKEN = os.environ.get("STRAPI_TOKEN", "")
HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

HEADERS = {"Authorization": f"Bearer {STRAPI_TOKEN}", "Content-Type": "application/json"}

def gorsel_uret(mekan_adi):
    prompt = f"Beautiful tourist photograph of {mekan_adi}, scenic landscape, professional travel photography, golden hour, 4k, highly detailed"
    print(f"   [ART] Gorsel uretiliyor: {mekan_adi}...")
    try:
        r = requests.post(HF_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": prompt}, timeout=180)
        if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
            print(f"   [OK] Gorsel uretildi ({len(r.content)} bytes)")
            return r.content
        elif r.status_code == 503:
            print("   [WAIT] Model yukleniyor, 30sn bekleniyor...")
            time.sleep(30)
            r = requests.post(HF_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": prompt}, timeout=180)
            if r.status_code == 200 and "image" in r.headers.get("content-type", ""):
                print(f"   [OK] Gorsel uretildi (2. deneme)")
                return r.content
        print(f"   [X] Gorsel hatasi (Kod: {r.status_code})")
        return None
    except Exception as e:
        print(f"   [X] Hata: {e}")
        return None

def yukle_ve_ekle(gorsel_bytes, dosya_adi, place_doc_id):
    # 1. Upload
    files = {"files": (dosya_adi, gorsel_bytes, "image/jpeg")}
    r = requests.post(f"{STRAPI_URL}/api/upload", headers={"Authorization": f"Bearer {STRAPI_TOKEN}"}, files=files, timeout=60)
    if r.status_code not in [200, 201]:
        print(f"   [X] Upload hatasi: {r.status_code}")
        return False
    media_id = r.json()[0]["id"]
    print(f"   [OK] Gorsel yuklendi (Media ID: {media_id})")

    # 2. Mekana bagla
    r2 = requests.put(
        f"{STRAPI_URL}/api/places/{place_doc_id}",
        headers=HEADERS,
        json={"data": {"KapakResmi": media_id}}
    )
    if r2.status_code == 200:
        print(f"   [OK] Gorsel mekana baglandi")
        # Publish
        requests.post(f"{STRAPI_URL}/api/places/{place_doc_id}/actions/publish", headers=HEADERS, json={})
        return True
    else:
        print(f"   [X] Baglama hatasi: {r2.text[:200]}")
        return False

# Mevcut mekanlari cek
print("=" * 50)
print("GORSEL EKLEME SCRIPTI")
print("=" * 50)

r = requests.get(f"{STRAPI_URL}/api/places?populate=KapakResmi&locale=tr&pagination[pageSize]=100", headers=HEADERS)
places = r.json().get("data", [])
print(f"\n>> {len(places)} mekan bulundu\n")

basarili = 0
for p in places:
    mekan_adi = p.get("MekanAdi", "?")
    doc_id = p.get("documentId")
    kapak = p.get("KapakResmi")

    if kapak:
        print(f"[YENIDEN] {mekan_adi} - eski gorsel degistiriliyor")

    print(f"\n[ISLEM] {mekan_adi}")
    gorsel = gorsel_uret(mekan_adi)
    if gorsel:
        dosya = f"{mekan_adi.replace(' ', '_').lower()}.jpg"
        if yukle_ve_ekle(gorsel, dosya, doc_id):
            basarili += 1
    time.sleep(3)

print(f"\n{'='*50}")
print(f"Tamamlandi! {basarili} mekana gorsel eklendi.")
