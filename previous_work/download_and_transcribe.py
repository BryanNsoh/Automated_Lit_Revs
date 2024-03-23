import os
import re
import aiosqlite
import fitz  # PyMuPDF
from scidownl import scihub_download
import requests
from bs4 import BeautifulSoup
from habanero import cn
import asyncio
import random
import time


# Function to remove special characters from a string
def remove_special_characters(text):
    return re.sub(r"[^a-zA-Z0-9\.\-]", "_", str(text))


def test_proxy(proxy):
    try:
        response = requests.get(
            "https://api.ipify.org?format=json", proxies=proxy, timeout=5
        )
        if response.status_code == 200:
            return True
    except requests.exceptions.RequestException:
        pass
    return False


async def scihub_download_pdf_async(doi, pdf_path, mirror, proxy):
    doi_url = f"https://doi.org/{doi}"
    if test_proxy(proxy):
        try:
            result = await asyncio.to_thread(
                scihub_download, doi_url, paper_type="doi", out=pdf_path, proxies=proxy
            )
            if result:
                return result
        except Exception as e:
            print(
                f"Scihub download failed for mirror {mirror} with proxy {proxy}: {str(e)}"
            )
    else:
        print(f"Proxy {proxy} is invalid")
    return None


async def scihub_download_pdf(doi, pdf_path, proxies):
    doi_url = f"https://doi.org/{doi}"
    mirrors = [
        "https://sci-hub.st/",
        "https://sci-hub.se/",
        "https://sci-hub.ru/",
        "https://sci-hub.tw/",
        "https://sci-hub.tf/",
        "https://sci-hub.mksa.top/",
        "https://sci-hub.ren/",
        "https://sci-hub.hkvisa.net/",
        "https://sci-hub.ltd/",
        "https://sci-hub.si/",
    ]
    random.shuffle(mirrors)

    tasks = []
    for mirror in mirrors:
        for proxy in proxies:
            task = asyncio.create_task(
                scihub_download_pdf_async(doi, pdf_path, mirror, proxy)
            )
            tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if result and not isinstance(result, Exception):
            return result

    return False


def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text


def download_from_unpaywall(doi, pdf_path):
    url = f"https://api.unpaywall.org/v2/{doi}?email=bnsoh2@unl.edu"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        is_oa = data.get("is_oa", False)

        if is_oa:
            best_oa_location = data.get("best_oa_location", {})
            pdf_url = best_oa_location.get("url")

            if pdf_url:
                pdf_response = requests.get(pdf_url)
                with open(pdf_path, "wb") as file:
                    file.write(pdf_response.content)
                return True

    return False


def scrape_text_from_doi(doi):
    doi_url = f"https://doi.org/{doi}"
    response = requests.get(doi_url)
    soup = BeautifulSoup(response.content, "html.parser")
    text = soup.get_text()

    if len(text.split()) >= 20:
        return text
    else:
        return None


def get_bibtex(doi):
    try:
        bibtex = cn.content_negotiation(ids=doi, format="bibtex")
        return bibtex
    except:
        return None


async def process_doi_async(
    doi,
    pdf_directory,
    proxies,
    semaphore,
    db_pool,
    retry_count=0,
    max_retries=1,
    backoff_factor=2,
    jitter_range=(0, 1),
):
    async with semaphore:
        filename = remove_special_characters(doi)
        pdf_path = os.path.join(pdf_directory, filename + ".pdf")
        text_path = os.path.join(pdf_directory, filename + ".txt")

        text = None
        pdf_location = None
        bibtex = get_bibtex(doi)

        # Try downloading PDF using scidownl with multiple mirrors and proxies
        if await scihub_download_pdf(doi, pdf_path, proxies):
            try:
                text = extract_text_from_pdf(pdf_path)
                pdf_location = pdf_path
                print(f"Scihub Download Successful {doi}")
            except Exception as e:
                print(f"Scihub Download Failed {doi}: {str(e)}")

        # Try downloading PDF from Unpaywall
        if not pdf_location and download_from_unpaywall(doi, pdf_path):
            try:
                text = extract_text_from_pdf(pdf_path)
                pdf_location = pdf_path
                print(f"Unpaywall download successful {doi}")
            except Exception as e:
                print(f"Unpaywall download failed {doi}: {str(e)}")

        # Try scraping text from DOI URL
        if not text:
            text = scrape_text_from_doi(doi)
            if text:
                with open(text_path, "w", encoding="utf-8") as file:
                    file.write(text)
                pdf_location = text_path
                print(f"Text scraping successful for DOI: {doi}")
            else:
                print(f"Text scraping failed for DOI: {doi}")

        if text:
            async with db_pool.acquire() as db_conn:
                async with db_conn.cursor() as cursor:
                    sql = "UPDATE filtered_query_results SET full_text = ?, pdf_location = ?, bibtex = ? WHERE doi = ?"
                    await cursor.execute(sql, (text, pdf_location, bibtex, doi[0]))
                    await db_conn.commit()

        if not text and retry_count < max_retries:
            # Exponential backoff with jitter
            await asyncio.sleep(
                backoff_factor**retry_count + random.uniform(*jitter_range)
            )
            return await process_doi_async(
                doi, pdf_directory, proxies, semaphore, db_pool, retry_count + 1
            )

        return text, pdf_location, bibtex


async def process_database_async(db_path, proxies, max_concurrent_requests=30):
    db_pool = await aiosqlite.connect(db_path)

    async with db_pool.cursor() as cursor:
        await cursor.execute(
            "SELECT doi FROM filtered_query_results WHERE doi IS NOT NULL AND doi != ''"
        )
        query_results = await cursor.fetchall()

    db_name = os.path.splitext(os.path.basename(db_path))[0]
    pdf_directory = os.path.join(os.path.dirname(db_path), db_name, "pdfs")
    os.makedirs(pdf_directory, exist_ok=True)

    semaphore = asyncio.Semaphore(max_concurrent_requests)
    tasks = []
    for (doi,) in query_results:
        task = asyncio.create_task(
            process_doi_async(doi, pdf_directory, proxies, semaphore, db_pool)
        )
        tasks.append(task)

    await asyncio.gather(*tasks)
    await db_pool.close()


async def process_searches_directory_async(proxies):
    searches_path = os.path.join(os.getcwd(), "searches")
    tasks = []
    for folder_name in os.listdir(searches_path):
        folder_path = os.path.join(searches_path, folder_name)
        if os.path.isdir(folder_path):
            for file_name in os.listdir(folder_path):
                if file_name.startswith("outline_") and file_name.endswith(".db"):
                    db_path = os.path.join(folder_path, file_name)
                    task = asyncio.create_task(process_database_async(db_path, proxies))
                    tasks.append(task)
    await asyncio.gather(*tasks)


# Proxy list
proxies = [
    {"http": "http://103.145.150.26:8080"},
    {"http": "http://95.216.57.120:8292"},
    {"http": "http://117.102.80.243:8080"},
    {"http": "http://124.83.74.218:8082"},
    {"http": "http://177.125.56.181:3128"},
    {"http": "http://45.70.236.150:999"},
    {"http": "http://190.94.212.125:999"},
    {"http": "http://146.190.224.33:3128"},
    {"http": "http://103.35.108.113:5020"},
    {"http": "http://103.188.168.66:8080"},
    {"http": "http://5.252.23.206:3128"},
    {"http": "http://185.208.102.55:8080"},
    {"http": "http://189.85.82.38:3128"},
    {"http": "http://190.94.212.149:999"},
    {"http": "http://186.156.161.235:3128"},
    {"http": "http://179.108.153.159:8080"},
    {"http": "http://190.90.7.195:8080"},
    {"http": "http://41.111.243.134:80"},
    {"http": "http://36.64.217.27:1313"},
    {"http": "http://103.168.129.123:8080"},
    {"http": "http://95.167.29.50:8080"},
    {"http": "http://186.115.202.103:8080"},
    {"http": "http://182.253.140.250:8080"},
    {"http": "http://114.9.24.46:3127"},
    {"http": "http://103.180.123.27:8080"},
    {"http": "http://200.32.64.126:999"},
    {"http": "http://103.8.164.16:80"},
    {"http": "http://103.191.115.238:84"},
    {"http": "http://103.211.107.91:8080"},
    {"http": "http://103.148.192.82:9012"},
    {"http": "http://103.179.246.30:8080"},
    {"http": "http://194.213.208.226:8180"},
    {"http": "http://102.213.223.46:82"},
    {"http": "http://111.225.152.95:8089"},
    {"http": "http://103.48.68.101:83"},
    {"http": "http://197.232.47.122:8080"},
    {"http": "http://139.162.224.37:3128"},
    {"http": "http://45.182.176.38:9947"},
    {"http": "http://114.8.131.178:8080"},
    {"http": "http://201.77.108.72:999"},
    {"http": "http://202.12.80.11:83"},
    {"http": "http://173.212.213.133:3128"},
    {"http": "http://95.47.119.122:8080"},
    {"http": "http://157.100.7.146:999"},
    {"http": "http://203.112.223.126:8080"},
    {"http": "http://41.76.111.18:3128"},
    {"http": "http://202.47.189.106:8080"},
    {"http": "http://5.187.9.10:8080"},
    {"http": "http://147.75.92.251:80"},
    {"http": "http://103.84.177.28:8083"},
    {"http": "http://45.174.79.232:999"},
    {"http": "http://103.155.54.26:82"},
]

# Start processing
loop = asyncio.get_event_loop()
loop.run_until_complete(process_searches_directory_async(proxies))
loop.close()
