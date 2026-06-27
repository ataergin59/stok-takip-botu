import json
import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from scraperHelpers import check_stock_zara, check_stock_bershka, check_stock_mango, check_stock_pullandbear, check_stock_stradivarius

# CONFIG YÜKLEME
with open("config.json", "r") as config_file:
    config = json.load(config_file)

urls_to_check = config.get("urls", [])
sizes_to_check = config.get("sizes_to_check", [])

# TELEGRAM BİLGİLERİNİ GİZLİDEN AL
BOT_API = os.environ.get("TELEGRAM_API")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not BOT_API or not CHAT_ID:
        print("Telegram API veya Chat ID eksik!")
        return
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            print("✅ Mesaj gönderildi.")
        else:
            print(f"❌ Telegram API hatası: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Telegram bağlantı hatası: {e}")

# TARAYICI AYARLARI
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

print("Bot başlatıldı (v2.2 - Boş URL temizleyicili)...")

try:
    for item in urls_to_check:
        url = item.get("url")
        store = item.get("store")
        
        # BOŞ URL TEMİZLEME: URL boşsa veya link değilse doğrudan atla
        if not url or len(url) < 10:
            continue
            
        try:
            print(f"Kontrol ediliyor: {store} - {url}")
            driver.get(url)
            time.sleep(5) 
            
            size_in_stock = None
            if store == "zara": size_in_stock = check_stock_zara(driver, sizes_to_check)
            elif store == "bershka": size_in_stock = check_stock_bershka(driver, sizes_to_check)
            elif store == "mango": size_in_stock = check_stock_mango(driver, sizes_to_check)
            elif store == "pullandbear": size_in_stock = check_stock_pullandbear(driver, sizes_to_check)
            elif store == "stradivarius": size_in_stock = check_stock_stradivarius(driver, sizes_to_check)
            
            if size_in_stock:
                send_telegram_message(f"🚨 STOK BULUNDU!\nMağaza: {store.upper()}\nBeden: {size_in_stock}\nLink: {url}")
            else:
                print(f"❌ {store} - Stok yok.")
        except Exception as e:
            print(f"Hata oluştu ({store}): {e}")

finally:
    driver.quit()
    print("İşlem tamamlandı.")
