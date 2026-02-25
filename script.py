import asyncio
from playwright.async_api import async_playwright

# Данные для заполнения формы
CITY = "с. Софіївська Борщагівка"
STREET = "вул. Січова"
HOUSE = "29"

async def select_autocomplete(page, selector, value):
    """Ввод текста по буквам и выбор первого варианта автокомплита"""
    input_el = page.locator(selector)
    try:
        await input_el.wait_for(state="visible", timeout=15000)
        await input_el.click()
        await input_el.fill("")  # очищаем поле
        for char in value:
            await input_el.type(char)
            await asyncio.sleep(0.15)  # имитация ввода по буквам
        # ждем появления списка автокомплита
        option = page.locator("li.ui-menu-item")  # пример списка, уточни под сайт
        await option.first.wait_for(state="visible", timeout=5000)
        await option.first.click()
    except Exception as e:
        print(f"Ошибка: поле {selector} не активное или автокомплит не появился. {e}")

async def make_screenshot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=100)  # headless=False для видимого браузера
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto("https://www.dtek-krem.com.ua/ua/shutdowns")

        # Закрываем поп-ап кликом в свободное место
        try:
            await page.mouse.click(10, 10)
            await asyncio.sleep(1)
        except:
            pass

        # Заполняем форму
        await select_autocomplete(page, "#locality_form", CITY)
        await select_autocomplete(page, "#street_form", STREET)
        await select_autocomplete(page, "#house", HOUSE)

        # Делаем скриншот
        await asyncio.sleep(2)  # чтобы график успел прогрузиться
        await page.screenshot(path="screenshot.png")
        print("Скриншот сделан!")

        await browser.close()

asyncio.run(make_screenshot())
