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

async def select_autocomplete(page, selector, text):
    """Вводимо текст в поле та обираємо перший варіант автокомпліту"""
    input_el = page.locator(selector)
    await input_el.click()
    await input_el.fill("")  # очистимо поле
    for char in text:
        await input_el.type(char, delay=100)  # вводимо по буквах
    # чекаємо поки з’явиться список автокомпліту
    dropdown_item = page.locator("ul[data-list] li").first
    await dropdown_item.wait_for(state="visible", timeout=5000)
    await dropdown_item.click()  # вибираємо перший варіант
    await page.wait_for_timeout(500)

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
        # Заповнюємо поля через автокомпліт
        # ===========================
        await select_autocomplete(page, "#locality_form", CITY)
        await select_autocomplete(page, "#street_form", STREET)
        await select_autocomplete(page, "#house", HOUSE)
        
        # Чекаємо поки графік згенерується
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
