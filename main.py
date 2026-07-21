import os
import json
import time
import requests
import undetected_chromedriver as uc
from dotenv import load_dotenv

from ScraperHelpers import (
    check_stock_zara, 
    check_stock_bershka, 
    check_stock_mango, 
    check_stock_pullandbear, 
    check_stock_stradivarius
)

load_dotenv()

BOT_API = os.getenv("TELEGRAM_API")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(message):
    if not BOT_API or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{BOT_API}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message}, timeout=15)

if __name__ == "__main__":
    try:
        with open("config.json", "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print("❌ config.json bulunamadı!")
        exit()

    urls_to_check = config.get("urls", [])
    sizes_to_check = config.get("sizes_to_check", [])

    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--headless=new") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    print("🚀 Giyim Stok Botu Başlatıldı...")
    
    driver = None
    try:
        driver = uc.Chrome(options=chrome_options, version_main=150)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for item in urls_to_check:
            url = item.get("url")
            store = item.get("store")
            
            if not url or len(url) < 10:
                continue
                
            try:
                print(f"\n🔍 Kontrol ediliyor: {store.upper()} -> {url}")
                driver.get(url)
                time.sleep(8) # Sayfanın yüklenmesi için biraz daha süre verdik
                
                # Sayfa başlığını yazdıralım (Engellenip engellenmediğimizi buradan anlarız)
                print(f"📄 Sayfa Başlığı: {driver.title}")
                
                size_in_stock = None
                
                if store == "zara": 
                    size_in_stock = check_stock_zara(driver, sizes_to_check)
                elif store == "bershka": 
                    size_in_stock = check_stock_bershka(driver, sizes_to_check)
                elif store == "mango": 
                    size_in_stock = check_stock_mango(driver, sizes_to_check)
                elif store == "pullandbear": 
                    size_in_stock = check_stock_pullandbear(driver, sizes_to_check)
                elif store == "stradivarius": 
                    size_in_stock = check_stock_stradivarius(driver, sizes_to_check)
                
                if size_in_stock:
                    print(f"🎉 STOK BULUNDU: {size_in_stock} beden!")
                    send_telegram_message(f"🚨 STOK BULUNDU!\nMağaza: {store.upper()}\nBeden: {size_in_stock}\nLink: {url}")
                else:
                    print(f"❌ {store.upper()} - Aranan beden stokta yok veya sayfa okunamadı.")
                    
            except Exception as e:
                print(f"❌ Hata ({store}): {e}")

    finally:
        if driver:
            driver.quit()
        print("\n🏁 İşlem tamamlandı.")
