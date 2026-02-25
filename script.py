import asyncio
import hashlib
from playwright.async_api import async_playwright
from telegram import Bot
from pathlib import Path
import os

# =========================
# 🔧 Налаштування
# =========================
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.dtek-krem.com.ua/ua/shutdowns"
CITY = "Кременчук"
STREET = "Соборна"
HOUSE = "15"

SCREENSHOT = "current.png"
HASH_FILE = "/github/home/.cache/power_monitor_hash.txt"  # GitHub cache location
Path(HASH_FILE).parent.mkdir(parents=True, exist_ok=True)

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

        # 🔹 Закриваємо поп-апи
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

        # 🔹 Клік + slow type
        await page.locator("#locality_form").click()
        await page.locator("#locality_form").type(CITY, delay=100)

        await page.locator("#street_form").click()
        await page.locator("#street_form").type(STREET, delay=100)

        await page.locator("input[name='house']").click()
        await page.locator("input[name='house']").type(HOUSE, delay=100)

        # 🔹 Пошук
        await page.locator("button[type='submit']").click()
        await page.wait_for_timeout(8000)

        # 🔹 Скрин
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
