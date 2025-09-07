# E-Lab Devs – Python Sitemap Crawler

Basit ama işlevsel bir **Python crawler**.  
Siteni tarar, bulduğu sayfalardan **dinamik `sitemap.xml`** üretir.  
Cloudflare arkasında çalışırken bile “lokalden tara → prod domaine yaz” mantığıyla kanonik URL’ler oluşturur.

> Developed & open-sourced by **E-Lab Devs**.

---

## ✨ Özellikler
- 🔎 BFS tarama (linkleri takip eder, döngüye girmez)
- 🌐 **Kanonik base**: Local/staging’den tarasan bile `<loc>` hep prod domain (ör. `https://www.elabdevs.com`)
- 🧹 Hariç tutma kuralları (admin, api, assets vs.)
- 🕒 `lastmod`: `HEAD` → `Last-Modified` varsa kullanır, yoksa UTC now
- ⚙️ `.env` ile konfigürasyon (domain, hız, limit vs.)
- 🧑‍💻 Cloudflare ile uyum (User-Agent / IP allow ile bypass)

---

## 📦 Gereksinimler
- Python **3.9+** (önerilen: 3.11)
- pip (güncel)
- (Opsiyonel) virtualenv

---

## 🚀 Kurulum
```bash
git clone https://github.com/elabdevs/elabdevs-crawler.git
cd elabdevs-crawler

# (opsiyonel) sanal ortam
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

---

## ⚙️ Konfigürasyon (.env)
```env
START_URL=http://localhost
CANONICAL_BASE=https://www.example.com
OUTPUT_PATH=/path/to/sitemap.xml

MAX_PAGES=1000
REQ_TIMEOUT=10
CRAWL_DELAY_SEC=0.2

EXCLUDE_PREFIXES=/admin,/login,/panel,/api,/uploads,/assets,/static,/storage

CRAWLER_UA=E-LabDevsCrawler/1.1 (+https://www.elabdevs.com)

CHANGEFREQ=weekly
PRIORITY=0.5
```

**Notlar:**
- `START_URL`: Cloudflare’ı bypass eden lokal/staging adresin (örn: `http://127.0.0.1:8080/`).
- `CANONICAL_BASE`: Sitemap’te yazılacak **asıl domain** (örn: `https://www.senin-domainin.com`).
- `OUTPUT_PATH`: Üretilen dosyanın yolu (web root içinde olmalı).
- `EXCLUDE_PREFIXES`: Sitemap’e girmesini istemediğin path’ler.
- `CRAWLER_UA`: Cloudflare/Firewall’da allow kuralı yazacaksan burada verdiğin UA’yı kullan.

---

## ▶️ Çalıştırma
```bash
python main.py
```

Başarılı çalışınca:
```
Toplam URL: 9
sitemap.xml yazıldı -> /path/to/sitemap.xml
```

---

## 🗂 robots.txt
Arama motorlarına konumu bildir:
```
Sitemap: https://www.example.com/sitemap.xml
```

---

## ⏰ Cron ile Otomatikleştirme
Her gece 03:00’te çalıştırmak için:
```bash
crontab -e
```
Satır ekle:
```
0 3 * * * /path/to/.venv/bin/python /path/to/main.py >> /var/log/sitemap_crawler.log 2>&1
```

> İpucu: Crawler bittiğinde Google’a ping atmak istersen, `main.py` sonunda şu GET isteğini çağırabilirsin:  
> `https://www.google.com/ping?sitemap=https://www.elabdevs.com/sitemap.xml`

---

## 🔐 Cloudflare Notları (403 görürsen)
- **Seçenek 1:** Crawler’ın çalıştığı **IP’yi Allow** et  
  Security → *Security rules / Tools* → **IP Access Rules** → *Allow* (sunucu IP: `curl ifconfig.me`).
- **Seçenek 2:** **User-Agent Allow**  
  Security → *Security rules* → *Create rule* → Expression:  
  ```
  (http.user_agent contains "E-LabDevsCrawler")
  ```
  Action: **Allow**  
- **Seçenek 3 (testlik):** Bot Fight Mode’u geçici olarak kapat.

---

## 🛠 Troubleshooting
**1) `TypeError: 'type' object is not subscriptable`**  
→ Python < 3.9 kullanıyorsun. 3.11’e yükselt veya `typing.List` kullan.

**2) `pip` import hataları**  
→ `pip` eski. Güncelle:
```bash
curl -sS https://bootstrap.pypa.io/get-pip.py | python3
```

**3) `403 Forbidden`**  
→ Cloudflare UA/IP izinlerini ayarla.

**4) `sitemap.xml` boş**  
- `START_URL` yanlış / HTML gelmiyor / JS ile render ediliyor olabilir.  
- `EXCLUDE_PREFIXES` çok agresif olabilir.  

**5) URL’ler `localhost` çıkıyor**  
→ `.env`’de `CANONICAL_BASE` doğru mu?

---

## 📜 Lisans
**MIT** – gönlünce kullan, forkla, geliştir.  
© E-Lab Devs

---

## 🙌 Katkı
Pull request’ler ve issue’lar açık.  
Projeyi faydalı bulduysan ⭐ vermeyi unutma!

---

### 🔎 Repo Description
> A simple Python-based web crawler that generates `sitemap.xml`.  
> Developed and open-sourced by **E-Lab Devs**.
