import asyncio
import hashlib
from pathlib import Path
import os
from telegram import Bot
from playwright.async_api import async_playwright

# =========================
# 🔧 Налаштування
# =========================
TOKEN = os.getenv("TOKEN")       # Telegram bot token
CHAT_ID = os.getenv("CHAT_ID")   # ваш chat id

URL = "https://www.dtek-krem.com.ua/ua/shutdowns"
CITY = "с. Софіївська Борщагівка"
STREET = "вул. Січова"
HOUSE = "29"

SCREENSHOT = "current.png"
HASH_FILE = ".cache/power_monitor_hash.txt"  # зберігаємо локально
Path(".cache").mkdir(parents=True, exist_ok=True)

# =========================

def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # 🔹 Закриваємо всі поп-апи
        await page.evaluate("""
            document.querySelectorAll('.modal, .popup, .overlay').forEach(el => el.remove());
        """)
        await page.wait_for_timeout(500)

        # 🔹 Робимо поля видимими
        await page.evaluate("""
            ['#locality_form','#street_form','input[name="house"]'].forEach(id => {
                const el = document.querySelector(id);
                if (el) { el.style.display='block'; el.removeAttribute('hidden'); }
            });
        """)
        await page.wait_for_timeout(500)

        # 🔹 Заповнюємо поля напряму + trigger input events для JS
        await page.evaluate(f"""
            const city = document.querySelector('#locality_form');
            const street = document.querySelector('#street_form');
            const house = document.querySelector('input[name="house"]');
            if (city) {{ city.value = "{CITY}"; city.dispatchEvent(new Event('input')) }}
            if (street) {{ street.value = "{STREET}"; street.dispatchEvent(new Event('input')) }}
            if (house) {{ house.value = "{HOUSE}"; house.dispatchEvent(new Event('input')) }}
        """)

        # 🔹 Чекаємо 5 секунд, щоб JS оновив графік
        await page.wait_for_timeout(5000)

        # 🔹 Робимо скріншот
        await page.screenshot(path=SCREENSHOT, full_page=True)
        await browser.close()

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

asyncio.run(main())
