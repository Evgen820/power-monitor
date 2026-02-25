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

def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

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
        await page.wait_for_timeout(1000)

        # Вибір населенного пункту
        await page.click('#locality_form')
        await page.fill('#locality_form', '')
        await page.type('#locality_form', CITY, delay=100)
        await page.wait_for_timeout(1500)
        option_city = page.locator(f'text="{CITY}"')
        if await option_city.count() > 0:
            await option_city.first.click()

        # Вибір вулиці
        await page.click('#street_form')
        await page.fill('#street_form', '')
        await page.type('#street_form', STREET, delay=100)
        await page.wait_for_timeout(1500)
        option_street = page.locator(f'text="{STREET}"')
        if await option_street.count() > 0:
            await option_street.first.click()

        # Введення номера будинку
        await page.fill('input[name="house"]', '')
        await page.type('input[name="house"]', HOUSE, delay=100)
        await page.wait_for_timeout(3000)  # чекаємо поки графік згенерується

        # Створюємо скріншот
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
