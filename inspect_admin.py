import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    os.makedirs('reports/admin_screenshots', exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        print("Navigating to admin panel...")
        await page.goto("https://tarihicengelkoytatlicisi.com.tr/admin")
        await page.wait_for_load_state("networkidle")

        print("Logging in...")
        await page.fill('input[type="email"], input[name="email"], input[id*="email"]', "cengelkoytatlicisi3431@gmail.com")
        await page.fill('input[type="password"], input[name="password"], input[id*="password"]', "35UZIL1Y")
        
        # Take a screenshot before clicking login
        await page.screenshot(path="reports/admin_screenshots/1_login_page.png")
        
        # Find and click the login button
        await page.click('button[type="submit"], input[type="submit"], button:has-text("Giriş"), a:has-text("Giriş")')
        
        print("Waiting for dashboard to load...")
        # Wait a bit for the redirect/dashboard loading
        await page.wait_for_timeout(5000)
        
        # Take screenshot of the dashboard
        await page.screenshot(path="reports/admin_screenshots/2_dashboard.png")
        
        # Try to extract some basic stats from the dashboard if any
        dashboard_text = await page.evaluate("() => document.body.innerText")
        with open("reports/admin_screenshots/dashboard_text.txt", "w", encoding="utf-8") as f:
            f.write(dashboard_text)
            
        print("Dashboard captured. Checking integrations if possible...")
        
        # Try to navigate or find "Entegrasyonlar" or "Ayarlar"
        nav_text = await page.evaluate("() => document.body.innerHTML")
        if "Entegrasyon" in nav_text or "Ayarlar" in nav_text:
            try:
                await page.click('text="Entegrasyon" >> nth=0')
                await page.wait_for_timeout(3000)
                await page.screenshot(path="reports/admin_screenshots/3_integrations.png")
            except Exception as e:
                print(f"Could not click Entegrasyon: {e}")
                
        await browser.close()
        print("Done. Check reports/admin_screenshots folder.")

if __name__ == "__main__":
    asyncio.run(main())
