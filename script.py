import asyncio
from playwright.async_api import async_playwright
from telegram import Bot

# Твої значення
TOKEN = "8307155981:AAEW0ZxzKgooySIjShzRq19IJ0V7I5uDVFQ"
CHAT_ID = 366025497

CITY = "с. Софіївська Борщагівка"
STREET = "вул. Січова"
HOUSE = "29"

async def select_autocomplete(page, selector, value):
    input_el = page.locator(selector)
    await input_el.wait_for(state="visible", timeout=30000)
    await page.wait_for_timeout(500)  # чекаємо, поки JS ініціалізує поле
    await input_el.click()
    await input_el.type(value, delay=100)  # вводимо по буквах
    # чекаємо поки з’явиться автокомпліт
    dropdown_item = page.locator("ul[data-list] li").first
    await dropdown_item.wait_for(state="visible", timeout=5000)
    await dropdown_item.click()

async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.dtek-krem.com.ua/ua/shutdowns", wait_until="networkidle")
        await page.wait_for_timeout(1000)

        # закриваємо поп-ап кліком за межами форми
        await page.mouse.click(10, 10)
        await page.wait_for_timeout(500)

        # вводимо дані
        await select_autocomplete(page, "#locality_form", CITY)
        await select_autocomplete(page, "#street_form", STREET)
        await select_autocomplete(page, "#house", HOUSE)

        # чекаємо, поки графік завантажиться
        await page.wait_for_selector(".graph-container", timeout=5000)

        # робимо скрін
        screenshot = await page.screenshot(full_page=True)
        await browser.close()
        return screenshot

async def main():
    screenshot = await make_screenshot()
    bot = Bot(token=TOKEN)
    await bot.send_photo(chat_id=CHAT_ID, photo=screenshot)

if __name__ == "__main__":
    asyncio.run(main())
