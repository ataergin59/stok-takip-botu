import os
import json
import time
import requests
from dotenv import load_dotenv
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ==========================================
# 1. GİZLİ BİLGİLERİ YÜKLEME (.env dosyasından)
# ==========================================
load_dotenv()

BOT_API = os.getenv("TELEGRAM_API")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    print("Telegram'a mesaj gönderme tetiklendi...")
    
    if not BOT_API or not CHAT_ID:
        print("❌ HATA: Telegram API veya Chat ID bulunamadı! Lütfen .env dosyasını kontrol et.")
        return
        
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    
    try:
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            print("✅ TELEGRAM MESAJI BAŞARIYLA GÖNDERİLDİ!")
        else:
            print(f"❌ Telegram API Hatası! Kod: {response.status_code} - Yanıt: {response.text}")
    except Exception as e:
        print(f"❌ Telegram Bağlantı Hatası: {e}")

# ==========================================
# 2. MAĞAZA STOK KONTROL FONKSİYONLARI
# ==========================================
def check_stock_zara(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 15)
        try:
            accept = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept.click()
        except: pass
        
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "size-selector-sizes")))
        size_elements = driver.find_elements(By.CSS_SELECTOR, "li[data-qa-qualifier='size-selector-sizes-size']")
        
        for li in size_elements:
            try:
                label = li.find_element(By.CSS_SELECTOR, "div[data-qa-qualifier='size-selector-sizes-size-label']").text.strip()
                if label in sizes_to_check:
                    button = li.find_element(By.CSS_SELECTOR, "button")
                    action = button.get_attribute("data-qa-action")
                    if action in ["size-in-stock", "size-low-on-stock"]:
                        return label
            except: continue
    except Exception as e:
        print(f"⚠️ Zara Element Bulunamadı: {type(e).__name__}")
    return None

def check_stock_bershka(driver, sizes_to_check):
    try:
        time.sleep(3)
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem'], li.size-item button")
        for btn in buttons:
            try:
                label = btn.find_element(By.CSS_SELECTOR, "span.text__label").text.strip()
                if label in sizes_to_check:
                    classes = btn.get_attribute("class") or ""
                    if "is-disabled" not in classes and btn.get_attribute("disabled") is None:
                        return label
            except: continue
    except Exception as e:
        print(f"⚠️ Bershka Element Bulunamadı: {type(e).__name__}")
    return None

def check_stock_mango(driver, sizes_to_check):
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='pdp.productInfo.sizeSelector.size']")
        for btn in buttons:
            label = btn.text.strip()
            if label in sizes_to_check:
                if "sizeAvailable" in btn.get_attribute("id") and btn.get_attribute("aria-disabled") == "false":
                    return label
    except Exception as e:
        print(f"⚠️ Mango Element Bulunamadı: {type(e).__name__}")
    return None

def check_stock_pullandbear(driver, sizes_to_check):
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem']")
        for btn in buttons:
            label = btn.text.strip()
            if label in sizes_to_check:
                if "is-disabled" not in btn.get_attribute("class"):
                    return label
    except: pass
    return None

def check_stock_stradivarius(driver, sizes_to_check):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "li[data-qa-anchor='sizeListItem']")
        for el in elements:
            label = el.text.strip()
            if label in sizes_to_check:
                classes = el.get_attribute("class") or ""
                if "is-disabled" not in classes and "sold-out" not in classes:
                    return label
    except: pass
    return None

import undetected_chromedriver as uc

# ... (Yukarıdaki fonksiyonların ve Telegram ayarların tamamen aynı kalacak) ...

# ==========================================
# 3. ANA ÇALIŞMA BLOĞU (GÜNCELLENDİ)
# ==========================================
try:
    with open("config.json", "r") as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    print("❌ config.json bulunamadı! Dosyanın main.py ile aynı klasörde olduğundan emin ol.")
    exit()

urls_to_check = config.get("urls", [])
sizes_to_check = config.get("sizes_to_check", [])

# ANTI-BOT TARAYICI AYARLARI
chrome_options = uc.ChromeOptions()
chrome_options.add_argument("--headless") # GitHub Actions için arka planda çalışma
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")

print("🚀 Bot başlatıldı (Anti-Bot Korumalı Sürüm)...")

# Bağlantı testi mesajı
send_telegram_message("🤖 Stok takip botu başlatıldı! Anti-bot sistemi aktif.")

try:
    # Sürücü ve tarayıcı sürümlerini eşitlemek için version_main eklendi
    driver = uc.Chrome(options=chrome_options, version_main=149)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    for item in urls_to_check:
        url = item.get("url")
        store = item.get("store")
        
        if not url or len(url) < 10:
            continue
            
        try:
            print(f"\n🔍 Kontrol ediliyor: {store.upper()} - {url}")
            driver.get(url)
            time.sleep(7) # Anti-bot ekranını geçmesi için süreyi biraz uzattık
            
            # --- YENİ EKLENEN TEŞHİS SATIRLARI ---
            print(f"📄 O anki Sayfa Başlığı: {driver.title}")
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text[:200]
                print(f"👀 Ekranda Görünen İlk Yazılar: {body_text.replace(chr(10), ' ')}")
            except:
                print("👀 Ekranda okunabilir bir metin bulunamadı!")
            # ------------------------------------
            
            size_in_stock = None
            if store == "zara": size_in_stock = check_stock_zara(driver, sizes_to_check)
            elif store == "bershka": size_in_stock = check_stock_bershka(driver, sizes_to_check)
            elif store == "mango": size_in_stock = check_stock_mango(driver, sizes_to_check)
            elif store == "pullandbear": size_in_stock = check_stock_pullandbear(driver, sizes_to_check)
            elif store == "stradivarius": size_in_stock = check_stock_stradivarius(driver, sizes_to_check)
            
            if size_in_stock:
                print(f"🎉 STOK BULUNDU: {size_in_stock} beden. Telegram'a iletiliyor...")
                send_telegram_message(f"🚨 STOK BULUNDU!\nMağaza: {store.upper()}\nBeden: {size_in_stock}\nLink: {url}")
            else:
                print(f"❌ {store.upper()} - Stok yok veya element bulunamadı.")
                
        except Exception as e:
            print(f"❌ Hata oluştu ({store}): {e}")

finally:
    # driver tanımlanmadan kod patlarsa quit() hata vermesin diye kontrol ekledik
    if 'driver' in locals():
        driver.quit()
    print("\n🏁 İşlem tamamlandı ve tarayıcı kapatıldı.")
