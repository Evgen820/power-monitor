import asyncio
from playwright.async_api import async_playwright
from telegram import Bot

# === Настройки ===
TOKEN = "8307155981:AAEW0ZxzKgooySIjShzRq19IJ0V7I5uDVFQ"
CHAT_ID = 366025497

CITY = "с. Софіївська Борщагівка"
STREET = "вул. Січова"
HOUSE = "29"

URL = "https://www.dtek-krem.com.ua/ua/shutdowns"
SCREENSHOT_PATH = "screenshot.png"

async def select_autocomplete(page, input_selector, full_text):
    try:
        input_el = page.locator(input_selector)
        await input_el.click(force=True)
        await asyncio.sleep(0.2)
        await input_el.type(full_text, delay=100)  # печатаем по буквам
        dropdown_item = page.locator(f"ul[data-list] li:has-text('{full_text}')")
        await dropdown_item.wait_for(state="hidden", timeout=5000)
        await dropdown_item.click()
    except Exception as e:
        print(f"Ошибка: поле {input_selector} не активне или автокомпліт не з’явився. {e}")

async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=800)
        page = await browser.new_page()
        await page.goto(URL)

        # Закрываем поп-ап кликом по свободной области
        try:
            await page.mouse.click(10, 10)
            await asyncio.sleep(0.3)
        except:
            pass
 
        await page.locator("text=Введіть нас. пункт").click()

       # Клік по населеному пункту
        
        await page.locator("role=textbox[name='Введіть нас. пункт']").fill("с. Софіївська Борщагівка")
        await page.locator("text=с. Софіївська Борщагівка").click()
# Клік по полю "Введіть вулицю"
        await page.locator("text=Введіть вулицю").click()

# Введення в поле "Введіть вулицю"
        await page.locator("role=textbox[name='Введіть вулицю']").fill("січ")

# Вибір із списку
        await page.locator("text=січ").click()

# Клік по полю "Номер будинку"
        await page.locator("role=textbox[name='Номер будинку']").click()

# Введення номера будинку
        await page.locator("role=textbox[name='Номер будинку']").fill("29")

# Вибір із списку (якщо з’являється)
        await page.locator("text=29").click()
       

  

        # Ждём, пока график появится (примерно)
        try:
            await page.wait_for_selector("#chart", timeout=5000)
        except:
            print("График не появился вовремя, делаем скриншот всё равно.")

        # Делаем скриншот
        await page.screenshot(path=SCREENSHOT_PATH, full_page=True)
        await browser.close()
        return SCREENSHOT_PATH

async def main():
    screenshot_file = await make_screenshot()

    # Отправляем через Telegram
    bot = Bot(token=TOKEN)
    with open(screenshot_file, "rb") as f:
        await bot.send_photo(chat_id=CHAT_ID, photo=f)

if __name__ == "__main__":
    asyncio.run(main())
