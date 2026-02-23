import asyncio
import os
from playwright.async_api import async_playwright

TIKTOK_USERNAME = "mkdigital260"
MESSAGE         = os.environ.get("MESSAGE", "Merci pour le like 🙌Si t'es intéressé(e) par l'ASA , envoie-moi un message avec \"INFO\" et je t'explique tout 👀")
MAX_DMS         = 20
DELAI_SECONDES  = 15

COOKIES = [
    {"name": "sessionid", "value": "96bf9b207e0d83d3ff488d190498d45c", "domain": ".tiktok.com", "path": "/"},
    {"name": "sessionid_ss", "value": "96bf9b207e0d83d3ff488d190498d45c", "domain": ".tiktok.com", "path": "/"},
    {"name": "sid_tt", "value": "96bf9b207e0d83d3ff488d190498d45c", "domain": ".tiktok.com", "path": "/"},
    {"name": "uid_tt", "value": "02ee70987a0edbaf886dd15ac96c317340643a266451a07062ed01894af58788", "domain": ".tiktok.com", "path": "/"},
    {"name": "uid_tt_ss", "value": "02ee70987a0edbaf886dd15ac96c317340643a266451a07062ed01894af58788", "domain": ".tiktok.com", "path": "/"},
    {"name": "tt_chain_token", "value": "R/13VDW3gcO3snYn6xGZFw==", "domain": ".tiktok.com", "path": "/"},
    {"name": "ttwid", "value": "1%7CNJgLAJnE5Ju5YhJ_PUcP28CTSnveT60lEOUkSfvxGdg%7C1771812406%7C7e27dc97daf5d991a0c6114d20ace70a652a0df34c2e948a966190aa6694fd60", "domain": ".tiktok.com", "path": "/"},
    {"name": "msToken", "value": "6x8mFewL9QB2D5zjwdHymqedYCnknOd1j-SYpB8Z2jErVssVEhmaHZ-m3lLB51WNm7Cn2G5lZ1bWZd5oGNQw_31uJNiyndQcdJDc2ti_Aez1Wu1OCNcpJTxPjzc_XnPf0Orfh8QiyfFJBOE=", "domain": ".tiktok.com", "path": "/"},
    {"name": "passport_csrf_token", "value": "ed72fe27d33c6a95374c9855c2932641", "domain": ".tiktok.com", "path": "/"},
]

async def get_all_videos(page):
    await page.goto(f"https://www.tiktok.com/@{TIKTOK_USERNAME}")
    await page.wait_for_timeout(4000)
    video_urls = []
    for _ in range(5):
        links = await page.query_selector_all('a[href*="/video/"]')
        for link in links:
            href = await link.get_attribute("href")
            if href and "/video/" in href and href not in video_urls:
                if not href.startswith("http"):
                    href = "https://www.tiktok.com" + href
                video_urls.append(href)
        await page.evaluate("window.scrollBy(0, 1000)")
        await page.wait_for_timeout(2000)
    print(f"📹 {len(video_urls)} vidéos trouvées")
    return video_urls

async def get_likers(page, video_url):
    await page.goto(video_url)
    await page.wait_for_timeout(5000)
    likers = []
    selectors = [
        '[data-e2e="like-count"]',
        '[data-e2e="browse-like-count"]',
        'strong[data-e2e="like-count"]',
        'span[data-e2e="like-count"]',
    ]
    clicked = False
    for selector in selectors:
        try:
            await page.click(selector, timeout=5000)
            clicked = True
            print(f"✅ Bouton likes trouvé avec: {selector}")
            break
        except:
            continue
    if not clicked:
        print(f"⚠️ Impossible d'ouvrir les likes pour {video_url}")
        return likers
    await page.wait_for_timeout(3000)
    users = await page.query_selector_all('[data-e2e="user-list-item"] a')
    for user in users:
        href = await user.get_attribute("href")
        if href and "/@" in href:
            username = href.split("/@")[-1].strip("/")
            if username not in likers and username != TIKTOK_USERNAME:
                likers.append(username)
    print(f"👥 {len(likers)} likers trouvés")
    return likers

async def send_dm(page, username):
    try:
        await page.goto(f"https://www.tiktok.com/@{username}")
        await page.wait_for_timeout(3000)
        msg_btn = await page.query_selector('[data-e2e="message-btn"]')
        if not msg_btn:
            print(f"⚠️ {username} — bouton message introuvable")
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
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        await context.add_cookies(COOKIES)
        print("🍪 Cookies injectés")
        page = await context.new_page()
        await page.goto("https://www.tiktok.com")
        await page.wait_for_timeout(4000)
        print("✅ Connecté via cookies")

        video_urls = await get_all_videos(page)
        deja_contactes = set()
        dms_envoyes = 0

        for video_url in video_urls:
            if dms_envoyes >= MAX_DMS:
                print(f"🛑 Limite de {MAX_DMS} DMs atteinte")
                break
            print(f"\n🎬 Traitement: {video_url}")
            likers = await get_likers(page, video_url)
            for username in likers:
                if dms_envoyes >= MAX_DMS:
                    break
                if username in deja_contactes:
                    print(f"⏭️ @{username} déjà contacté")
                    continue
                succes = await send_dm(page, username)
                deja_contactes.add(username)
                if succes:
                    dms_envoyes += 1
                await asyncio.sleep(DELAI_SECONDES)

        print(f"\n🎉 Session terminée — {dms_envoyes} DMs envoyés")
        await browser.close()

asyncio.run(run_agent())
