import asyncio
from playwright.async_api import async_playwright
from telegram import Bot

# ================== Налаштування ==================
TOKEN = "8307155981:AAEW0ZxzKgooySIjShzRq19IJ0V7I5uDVFQ"
CHAT_ID = 366025497

CITY = "с. Софіївська Борщагівка"
STREET = "вул. Січова"
HOUSE = "29"

SCREENSHOT_FILE = "power.png"

# ================== Функції ==================
async def select_autocomplete(page, selector, value):
    input_el = page.locator(selector)
    # чекаємо, поки елемент існує у DOM
    await input_el.wait_for(state="attached", timeout=30000)
    await page.wait_for_timeout(1000)  # даємо JS час ініціалізувати поле

    # клік "force" щоб обійти блокування стилями
    await input_el.click(force=True)
    await input_el.fill("")  # очищуємо поле
    await input_el.type(value, delay=100)

    # чекаємо появи першого варіанту автокомпліту
    dropdown_item = page.locator("ul[data-list] li").first
    await dropdown_item.wait_for(state="visible", timeout=5000)
    await dropdown_item.click()

async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.dtek-krem.com.ua/ua/shutdowns")

        # закриваємо поп-ап кліком за межами форми
        await page.mouse.click(10, 10)
        await page.wait_for_timeout(1500)

        # вводимо дані у поля
        await select_autocomplete(page, "#locality_form", CITY)
        await select_autocomplete(page, "#street_form", STREET)
        await select_autocomplete(page, "#house", HOUSE)

        # чекаємо, поки графік з’явиться
        graph = page.locator("#chart-container")  # контейнер графіка
        await graph.wait_for(state="visible", timeout=10000)

        # робимо скріншот графіка
        await graph.screenshot(path=SCREENSHOT_FILE)
        await browser.close()
        return SCREENSHOT_FILE

async def main():
    screenshot = await make_screenshot()
    bot = Bot(token=TOKEN)
    with open(screenshot, "rb") as f:
        await bot.send_photo(chat_id=CHAT_ID, photo=f)

# ================== Запуск ==================
asyncio.run(main())
