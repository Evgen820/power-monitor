import asyncio
import hashlib
import os
from playwright.async_api import async_playwright
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

URL = "https://www.dtek-krem.com.ua/ua/shutdowns"

CITY = "с. Софіївська Борщагівка"
STREET = "вул. Січова"
HOUSE = "29"

HASH_FILE = "last_hash.txt"
SCREENSHOT = "current.png"

def get_hash(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL, timeout=60000)

        # чекаємо завершення JS
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)

        # видаляємо поп-апи
        await page.evaluate("""
            document.querySelectorAll('.modal, .popup, .overlay').forEach(el => el.remove());
        """)
        await page.wait_for_timeout(2000)

        # чекаємо видимість і заповнюємо форму
        await page.locator("#locality_form").wait_for(state="visible", timeout=10000)
        await page.locator("#locality_form").fill(CITY)
        await page.wait_for_timeout(1000)

        await page.locator("#street_form").wait_for(state="visible", timeout=10000)
        await page.locator("#street_form").fill(STREET)
        await page.wait_for_timeout(1000)

        await page.locator("input[name='house']").wait_for(state="visible", timeout=10000)
        await page.locator("input[name='house']").fill(HOUSE)
        await page.wait_for_timeout(1000)

        # натискаємо кнопку пошуку
        await page.locator("button[type='submit']").click()
        await page.wait_for_timeout(8000)

        # робимо скрін
        await page.screenshot(path=SCREENSHOT, full_page=True)
        await browser.close()

async def main():
    await make_screenshot()
    new_hash = get_hash(SCREENSHOT)

    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            old_hash = f.read()
    else:
        old_hash = ""

    if new_hash != old_hash:
        bot = Bot(token=TOKEN)
        await bot.send_photo(chat_id=CHAT_ID, photo=open(SCREENSHOT, "rb"))
        with open(HASH_FILE, "w") as f:
            f.write(new_hash)

asyncio.run(main())
