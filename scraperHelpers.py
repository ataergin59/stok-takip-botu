from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time

# --- ZARA ---
def check_stock_zara(driver, sizes_to_check):
    try:
        wait = WebDriverWait(driver, 15)
        try:
            accept = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
            accept.click()
        except: 
            pass
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
            except: 
                continue
    except Exception as e:
        print(f"Zara hata: {e}")
    return None

# --- BERSHKA ---
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
            except: 
                continue
    except Exception as e:
        print(f"Bershka hata: {e}")
    return None

# --- MANGO ---
def check_stock_mango(driver, sizes_to_check):
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[id^='pdp.productInfo.sizeSelector.size']")
        for btn in buttons:
            label = btn.text.strip()
            if label in sizes_to_check:
                if "sizeAvailable" in btn.get_attribute("id") and btn.get_attribute("aria-disabled") == "false":
                    return label
    except Exception as e:
        print(f"Mango hata: {e}")
    return None

# --- PULL&BEAR ---
def check_stock_pullandbear(driver, sizes_to_check):
    try:
        buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-qa-anchor='sizeListItem']")
        for btn in buttons:
            label = btn.text.strip()
            if label in sizes_to_check:
                if "is-disabled" not in btn.get_attribute("class"):
                    return label
    except: 
        pass
    return None

# --- STRADIVARIUS ---
def check_stock_stradivarius(driver, sizes_to_check):
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, "li[data-qa-anchor='sizeListItem']")
        for el in elements:
            label = el.text.strip()
            if label in sizes_to_check:
                classes = el.get_attribute("class") or ""
                if "is-disabled" not in classes and "sold-out" not in classes:
                    return label
    except: 
        pass
    return None
