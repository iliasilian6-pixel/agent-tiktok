import asyncio
import os
import json
from playwright.async_api import async_playwright

VIDEO_URL      = os.environ.get("VIDEO_URL", "https://www.tiktok.com/@ton_compte/video/ID")
MESSAGE        = os.environ.get("MESSAGE", "Merci pour le like !")
MAX_DMS        = 20
DELAI_SECONDES = 15

COOKIES = [
    {"name": "sessionid", "value": "96bf9b207e0d83d3ff488d190498d45c", "domain": ".tiktok.com", "path": "/"},
    {"name": "sessionid_ss", "value": "96bf9b207e0d83d3ff488d190498d45c", "domain": ".tiktok.com", "path": "/"},
    {"name": "sid_tt", "value": "96bf9b207e0d83d3ff488d190498d45c", "domain": ".tiktok.com", "path": "/"},
    {"name": "sid_guard", "value": "96bf9b207e0d83d3ff488d190498d45c%7C1771812402%7C15552000%7CSat%2C+22-Aug-2026+02%3A06%3A42+GMT", "domain": ".tiktok.com", "path": "/"},
    {"name": "uid_tt", "value": "02ee70987a0edbaf886dd15ac96c317340643a266451a07062ed01894af58788", "domain": ".tiktok.com", "path": "/"},
    {"name": "uid_tt_ss", "value": "02ee70987a0edbaf886dd15ac96c317340643a266451a07062ed01894af58788", "domain": ".tiktok.com", "path": "/"},
    {"name": "tt_chain_token", "value": "R/13VDW3gcO3snYn6xGZFw==", "domain": ".tiktok.com", "path": "/"},
    {"name": "ttwid", "value": "1%7CNJgLAJnE5Ju5YhJ_PUcP28CTSnveT60lEOUkSfvxGdg%7C1771812406%7C7e27dc97daf5d991a0c6114d20ace70a652a0df34c2e948a966190aa6694fd60", "domain": ".tiktok.com", "path": "/"},
    {"name": "msToken", "value": "6x8mFewL9QB2D5zjwdHymqedYCnknOd1j-SYpB8Z2jErVssVEhmaHZ-m3lLB51WNm7Cn2G5lZ1bWZd5oGNQw_31uJNiyndQcdJDc2ti_Aez1Wu1OCNcpJTxPjzc_XnPf0Orfh8QiyfFJBOE=", "domain": ".tiktok.com", "path": "/"},
    {"name": "passport_csrf_token", "value": "ed72fe27d33c6a95374c9855c2932641", "domain": ".tiktok.com", "path": "/"},
]

async def get_likers(page):
    await page.goto(VIDEO_URL)
    await page.wait_for_timeout(5000)
    likers = []
    try:
        await page.click('[data-e2e="like-count"]', timeout=10000)
    except:
        try:
            await page.click('[data-e2e="browse-like-count"]', timeout=10000)
        except:
            print("⚠️ Impossible d'ouvrir la liste des likes")
            return likers
    await page.wait_for_timeout(3000)
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

        # Injection des cookies de session
        await context.add_cookies(COOKIES)
        print("🍪 Cookies injectés")

        page = await context.new_page()
        await page.goto("https://www.tiktok.com")
        await page.wait_for_timeout(4000)
        print("✅ Connecté via cookies")

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
