# -*- coding: utf-8 -*-
# gorselleri uretip images/ klasorune kaydeder
import requests, sys, io, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HF_TOKEN = os.environ.get("HF_TOKEN", "")
HF_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

MEKANLAR = [
    "Olimpos Antik Kenti",
    "Kas Marina",
    "Demre Myra Antik Kenti",
    "Grand Canyon",
    "Cadillac Ranch",
    "Santa Monica Pier"
]

for mekan in MEKANLAR:
    dosya = f"images/{mekan.replace(' ','_').lower()}.jpg"
    if os.path.exists(dosya):
        print(f"[SKIP] {mekan} - zaten var")
        continue

    print(f"[URET] {mekan}...")
    prompt = f"Beautiful tourist photograph of {mekan}, scenic landscape, travel photography, golden hour, 4k"
    
    for d in range(3):
        try:
            r = requests.post(HF_URL, headers={"Authorization": f"Bearer {HF_TOKEN}"}, json={"inputs": prompt}, timeout=180)
            if r.status_code == 200 and "image" in r.headers.get("content-type",""):
                with open(dosya, "wb") as f:
                    f.write(r.content)
                print(f"   [OK] {len(r.content)} bytes -> {dosya}")
                break
            elif r.status_code == 503:
                print(f"   [WAIT] Model yukleniyor...")
                time.sleep(30)
            else:
                print(f"   [X] Hata: {r.status_code}")
                break
        except Exception as e:
            print(f"   [X] {e}")
    time.sleep(2)

print("\nBitti! Simdi 'git add images/ && git commit && git push' yap.")
