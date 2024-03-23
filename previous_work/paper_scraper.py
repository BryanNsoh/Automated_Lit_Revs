import os
import json
import requests


class ScholarPaperDownloader:
    def __init__(self, download_path="./downloads"):
        self.download_path = download_path
        if not os.path.exists(download_path):
            os.makedirs(download_path)

    def load_json_files(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                with open(os.path.join(directory, filename), "r") as file:
                    yield json.load(file)

    def get_doi_from_title(self, title):
        url = f"https://api.crossref.org/works?query.title={title}&rows=1"
        response = requests.get(url)

        if response.status_code == 200:
            data = json.loads(response.text)
            items = data["message"]["items"]
            if items:
                return items[0]["DOI"]

        return None

    def download_paper(self, doi):
        download_cmd = f'scidownl download --doi {doi} --out {self.download_path}/{doi.replace("/", "_")}.pdf'
        os.system(download_cmd)

    def process_directory(self, directory):
        for json_data in self.load_json_files(directory):
            for result in json_data["organic_results"]:
                title = result["title"]
                doi = self.get_doi_from_title(title)
                if doi:
                    self.download_paper(doi)
                else:
                    print(f"No DOI found for the title: {title}")


# Usage
downloader = ScholarPaperDownloader()
downloader.process_directory("path_to_your_json_directory")
