import asyncio
import hashlib
from pathlib import Path
import os
from telegram import Bot
from playwright.async_api import async_playwright

# =========================
# 🔧 Налаштування
# =========================
TOKEN = "8307155981:AAEW0ZxzKgooySIjShzRq19IJ0V7I5uDVFQ"
CHAT_ID = 366025497

URL = "https://www.dtek-krem.com.ua/ua/shutdowns"
CITY = "с. Софіївська Борщагівка"
STREET = "вул. січова"
HOUSE = "29"

SCREENSHOT = "current.png"
HASH_FILE = ".cache/power_monitor_hash.txt"
Path(".cache").mkdir(parents=True, exist_ok=True)

# =========================
# Допоміжні функції
# =========================
def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

# =========================
# Основна функція
# =========================
async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Відкриваємо сайт
        await page.goto(URL, timeout=60000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # Закриваємо поп-ап кліком поза формою
        await page.mouse.click(10, 10)
        await page.wait_for_timeout(1500)

        # ===========================
        # Заповнюємо поля через JS
        # ===========================
        await page.evaluate(f"""
            (() => {{
                // Населений пункт
                const cityInput = document.querySelector('#locality_form');
                cityInput.value = "{CITY}";
                cityInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                // Вулиця
                const streetInput = document.querySelector('#street_form');
                streetInput.value = "{STREET}";
                streetInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                
                // Будинок
                const houseInput = document.querySelector('#house');
                houseInput.value = "{HOUSE}";
                houseInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }})();
        """)
        
        # Чекаємо поки графік підвантажиться
        await page.wait_for_timeout(4000)

        # ===========================
        # Скриншот
        # ===========================
        await page.screenshot(path=SCREENSHOT, full_page=True)
        await browser.close()

# =========================
# Основний цикл
# =========================
async def main():
    await make_screenshot()
    new_hash = get_hash(SCREENSHOT)

    if Path(HASH_FILE).exists():
        old_hash = Path(HASH_FILE).read_text()
    else:
        old_hash = ""

    if new_hash != old_hash:
        bot = Bot(token=TOKEN)
        await bot.send_photo(chat_id=CHAT_ID, photo=open(SCREENSHOT, "rb"))
        Path(HASH_FILE).write_text(new_hash)

# =========================
# Запуск
# =========================
asyncio.run(main())
