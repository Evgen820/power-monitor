import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from telegram import Bot

# --- Налаштування ---
TOKEN = "8307155981:AAEW0ZxzKgooySIjShzRq19IJ0V7I5uDVFQ"
CHAT_ID = 366025497

CITY = "с. Софіївська Борщагівка"
STREET = "вул. Січова"
HOUSE = "29"

URL = "https://www.dtek-krem.com.ua/ua/shutdowns"
SCREENSHOT_PATH = "screenshot.png"

# --- Функція для автокомпліту ---
async def select_autocomplete(page, selector, value):
    input_el = page.locator(selector)
    try:
        # чекаємо, поки елемент прикріпиться до DOM
        await input_el.wait_for(state="attached", timeout=30000)
        await page.wait_for_timeout(1500)  # даємо JS активувати поле

        # force-клік
        await input_el.click(force=True)
        # очищення через backspace
        await input_el.type("\b" * 20, delay=50)
        # вводимо текст
        await input_el.type(value, delay=100)

        # чекаємо і вибираємо перший варіант автокомпліту
        dropdown_item = page.locator("ul[data-list] li").first
        await dropdown_item.wait_for(state="visible", timeout=5000)
        await dropdown_item.click()
    except PlaywrightTimeoutError:
        print(f"Помилка: поле {selector} не активне або автокомпліт не з’явився.")

# --- Основна функція ---
async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(URL)

        # Закриваємо поп-ап клікнувши поза формою
        await page.mouse.click(10, 10)
        await page.wait_for_timeout(1000)  # даємо час на анімацію

        # Заповнюємо поля
        await select_autocomplete(page, "#locality_form", CITY)
        await select_autocomplete(page, "#street_form", STREET)
        await select_autocomplete(page, "#house", HOUSE)

        # Даємо час JS відмалювати графік
        await page.wait_for_timeout(2000)

        # Скриншот графіка
        await page.screenshot(path=SCREENSHOT_PATH)
        await browser.close()

    return SCREENSHOT_PATH

# --- Відправка в Telegram ---
async def main():
    screenshot = await make_screenshot()
    bot = Bot(token=TOKEN)
    with open(screenshot, "rb") as f:
        bot.send_photo(chat_id=CHAT_ID, photo=f)
    print("Скріншот надіслано.")

# --- Запуск ---
if __name__ == "__main__":
    asyncio.run(main())
