import asyncio
import os
from playwright.async_api import async_playwright

TIKTOK_USERNAME = os.environ.get("TIKTOK_USERNAME", "ton_username")
TIKTOK_PASSWORD = os.environ.get("TIKTOK_PASSWORD", "ton_mot_de_passe")
VIDEO_URL       = os.environ.get("VIDEO_URL", "https://www.tiktok.com/@ton_compte/video/ID")
MESSAGE         = os.environ.get("MESSAGE", "Merci pour ton like ! 🙏")
MAX_DMS         = 20
DELAI_SECONDES  = 15

async def login(page):
    await page.goto("https://www.tiktok.com/login/phone-or-email/email")
    await page.wait_for_timeout(3000)
    await page.fill('input[name="username"]', TIKTOK_USERNAME)
    await page.fill('input[type="password"]', TIKTOK_PASSWORD)
    await page.click('button[type="submit"]')
    await page.wait_for_timeout(5000)
    print("✅ Connecté à TikTok")

async def get_likers(page):
    await page.goto(VIDEO_URL)
    await page.wait_for_timeout(3000)
    await page.click('[data-e2e="like-count"]')
    await page.wait_for_timeout(2000)
    likers = []
    users = await page.query_selector_all('[data-e2e="user-list-item"] a')
    for user in users:
        href = await user.get_attribute("href")
        if href and "/@" in href:
            username = href.split("/@")[-1].strip("/")
            if username not in likers:
                likers.append(username)
    print(f"👥 {len(likers)} likers trouvés")
    return likers

async def send_dm(page, username):
    try:
        await page.goto(f"https://www.tiktok.com/@{username}")
        await page.wait_for_timeout(3000)
        msg_btn = await page.query_selector('[data-e2e="message-btn"]')
        if not msg_btn:
            print(f"⚠️ {username} — compte privé ou bouton introuvable")
            return False
        await msg_btn.click()
        await page.wait_for_timeout(2000)
        await page.keyboard.type(MESSAGE)
        await page.wait_for_timeout(1000)
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(2000)
        print(f"✅ DM envoyé à @{username}")
        return True
    except Exception as e:
        print(f"❌ Erreur avec @{username} : {e}")
        return False

async def run_agent():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        await login(page)
        likers = await get_likers(page)
        dms_envoyes = 0
        for username in likers:
            if dms_envoyes >= MAX_DMS:
                break
            succes = await send_dm(page, username)
            if succes:
                dms_envoyes += 1
            await asyncio.sleep(DELAI_SECONDES)
        print(f"🎉 {dms_envoyes} DMs envoyés")
        await browser.close()

asyncio.run(run_agent())
