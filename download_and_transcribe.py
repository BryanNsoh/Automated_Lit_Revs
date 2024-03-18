import os
import re
import sqlite3
import fitz  # PyMuPDF
from scidownl import scihub_download
import requests
from bs4 import BeautifulSoup
from habanero import cn
import asyncio
import concurrent.futures
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
    retry_count=0,
    max_retries=3,
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
        if scihub_download_pdf(doi, pdf_path, proxies):
            try:
                text = extract_text_from_pdf(pdf_path)
                pdf_location = pdf_path
            except Exception as e:
                print(f"Scihub Download Failed {doi}: {str(e)}")

        # Try downloading PDF from Unpaywall
        if not pdf_location and download_from_unpaywall(doi, pdf_path):
            try:
                text = extract_text_from_pdf(pdf_path)
                pdf_location = pdf_path
            except Exception as e:
                print(f"Unpaywall download failed {doi}: {str(e)}")

        # Try scraping text from DOI URL
        if not text:
            text = scrape_text_from_doi(doi)
            if text:
                with open(text_path, "w", encoding="utf-8") as file:
                    file.write(text)
                pdf_location = text_path
            else:
                print(f"Text scraping failed for DOI: {doi}")

        if not text and retry_count < max_retries:
            # Exponential backoff with jitter
            await asyncio.sleep(
                backoff_factor**retry_count + random.uniform(*jitter_range)
            )
            return await process_doi_async(
                doi, pdf_directory, proxies, semaphore, retry_count + 1
            )

        return text, pdf_location, bibtex


async def process_database_async(db_path, proxies, max_concurrent_requests=10):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT doi FROM filtered_query_results WHERE doi IS NOT NULL AND doi != ''"
    )
    query_results = cursor.fetchall()

    db_name = os.path.splitext(os.path.basename(db_path))[0]
    pdf_directory = os.path.join(os.path.dirname(db_path), db_name, "pdfs")
    os.makedirs(pdf_directory, exist_ok=True)

    semaphore = asyncio.Semaphore(max_concurrent_requests)
    tasks = []
    for (doi,) in query_results:
        task = asyncio.create_task(
            process_doi_async(doi, pdf_directory, proxies, semaphore)
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for doi, result in zip(query_results, results):
        if isinstance(result, Exception):
            print(f"Error processing DOI {doi}: {str(result)}")
        else:
            text, pdf_location, bibtex = result
            if text:
                cursor.execute(
                    "UPDATE filtered_query_results SET full_text = ?, pdf_location = ?, bibtex = ? WHERE doi = ?",
                    (text, pdf_location, bibtex, doi),
                )
                conn.commit()

    conn.close()


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
    {"http": "http://180.183.157.159:8080"},
    {"http": "socks5://46.4.96.137:1080"},
    {"http": "socks5://47.91.88.100:1080"},
    {"http": "socks5://45.77.56.114:30205"},
    {"http": "socks5://82.196.11.105:1080"},
    {"https": "https://51.254.69.243:3128"},
    {"http": "socks5://178.62.193.19:1080"},
    {"http": "socks5://188.226.141.127:1080"},
    {"http": "socks5://217.23.6.40:1080"},
    {"http": "socks5://185.153.198.226:32498"},
    {"https": "https://81.171.24.199:3128"},
    {"http": "socks5://5.189.224.84:10000"},
    {"http": "socks5://108.61.175.7:31802"},
    {"https": "https://176.31.200.104:3128"},
    {"https": "https://83.77.118.53:17171"},
    {"https": "https://173.192.21.89:80"},
    {"https": "https://163.172.182.164:3128"},
    {"https": "https://163.172.168.124:3128"},
    {"https": "https://164.68.105.235:3128"},
    {"https": "https://5.199.171.227:3128"},
    {"https": "https://93.171.164.251:8080"},
    {"https": "https://212.112.97.27:3128"},
    {"https": "https://51.68.207.81:80"},
    {"https": "https://91.211.245.176:8080"},
    {"https": "https://84.201.254.47:3128"},
    {"https": "https://95.156.82.35:3128"},
    {"https": "https://185.118.141.254:808"},
    {"http": "socks5://164.68.98.169:9300"},
    {"https": "https://217.113.122.142:3128"},
    {"https": "https://188.100.212.208:21129"},
    {"https": "https://83.77.118.53:17171"},
    {"https": "https://83.79.50.233:64527"},
]

# Start processing
asyncio.run(process_searches_directory_async(proxies))
