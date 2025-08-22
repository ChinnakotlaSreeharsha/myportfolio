# main/management/commands/fetch_linkedin_certs.py
from django.core.management.base import BaseCommand
from main.models import Certification
from playwright.async_api import async_playwright
from asgiref.sync import sync_to_async
from django.core.files.base import ContentFile
import aiohttp
import asyncio
import re
import os
from urllib.parse import urlparse


class Command(BaseCommand):
    help = "Fetch LinkedIn certifications with issuer logos using Playwright"

    async def download_image(self, url):
        """Download image from URL and return Django ContentFile"""
        if not url:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = await resp.read()
                        return ContentFile(data)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"Failed to download image {url}: {e}"))
        return None

    async def fetch_certs(self):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(storage_state="storage_state.json")
            page = await context.new_page()

            # Go to LinkedIn certifications page
            await page.goto(
                "https://www.linkedin.com/in/chinnakotla-sree-harsha-85502620b/details/certifications/"
            )
            await page.wait_for_timeout(5000)  # wait for page to load

            cert_elements = await page.query_selector_all("li.pvs-list__paged-list-item")
            certs = []

            for el in cert_elements:
                # Name
                name_el = await el.query_selector("span[aria-hidden='true']")
                name = (await name_el.inner_text()).strip() if name_el else None

                # Issuer
                issuer_el = await el.query_selector("span.t-14.t-normal")
                issuer = (await issuer_el.inner_text()).strip() if issuer_el else None

                # Issue Date
                issue_el = await el.query_selector("span.t-14.t-normal.t-black--light")
                issue_text = (await issue_el.inner_text()).strip() if issue_el else ""
                issue_month, issue_year = None, None
                if issue_text:
                    match = re.search(r"([A-Za-z]+)\s(\d{4})", issue_text)
                    if match:
                        issue_month, issue_year = match.groups()
                    else:
                        match = re.search(r"(\d{4})", issue_text)
                        if match:
                            issue_year = match.group(1)

                # Expiration Date
                exp_el = await el.query_selector("span:has-text('Expires')")
                exp_text = (await exp_el.inner_text()).replace("Expires ", "").strip() if exp_el else ""
                exp_month, exp_year = None, None
                if exp_text:
                    match = re.search(r"([A-Za-z]+)\s(\d{4})", exp_text)
                    if match:
                        exp_month, exp_year = match.groups()
                    else:
                        match = re.search(r"(\d{4})", exp_text)
                        if match:
                            exp_year = match.group(1)

                # Credential ID
                cred_id_el = await el.query_selector("span:has-text('Credential ID')")
                cred_id = (await cred_id_el.inner_text()).replace("Credential ID ", "").strip() if cred_id_el else None

                # Credential URL
                url_el = await el.query_selector_all("a")
                credential_url = None
                for link in url_el:
                    href = await link.get_attribute("href")
                    if href and ("certificate" in href or "cert" in href):
                        credential_url = href
                        break

                # Issuer Logo
                logo_el = await el.query_selector("img")
                issuer_logo_url = await logo_el.get_attribute("src") if logo_el else None

                if name:
                    certs.append({
                        "name": name,
                        "issuer": issuer,
                        "issue_date_month": issue_month,
                        "issue_date_year": issue_year,
                        "expiration_date_month": exp_month,
                        "expiration_date_year": exp_year,
                        "credential_id": cred_id,
                        "credential_url": credential_url,
                        "issuer_logo_url": issuer_logo_url
                    })

            await browser.close()
            return certs

    def handle(self, *args, **options):
        async def main():
            # Delete old certifications
            await sync_to_async(Certification.objects.all().delete)()

            certs = await self.fetch_certs()
            for cert in certs:
                # Download logo image
                issuer_logo_file = await self.download_image(cert.get("issuer_logo_url"))

                obj = Certification(
                    name=cert["name"],
                    issuer=cert["issuer"],
                    issue_date_month=cert["issue_date_month"],
                    issue_date_year=cert["issue_date_year"],
                    expiration_date_month=cert["expiration_date_month"],
                    expiration_date_year=cert["expiration_date_year"],
                    credential_id=cert["credential_id"],
                    credential_url=cert["credential_url"]
                )

                # Save issuer logo
                if issuer_logo_file:
                    # Use a clean filename
                    filename = cert["issuer"].replace(" ", "_") + ".jpg" if cert["issuer"] else "logo.jpg"
                    obj.issuer_logo.save(filename, issuer_logo_file, save=False)

                await sync_to_async(obj.save)()

            self.stdout.write(self.style.SUCCESS(f"✅ Imported {len(certs)} certifications with logos."))

        asyncio.run(main())
