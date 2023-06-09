import logging
import re
from typing import Dict, List

import requests


class KnowUnity:
    API_ENDPOINT = "https://apiedge-eu-central-1.knowunity.com/knows/"
    UUID_REGEX = r"[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"

    def __init__(self, url: str):
        self.url = url
        self.uuid = self.extract_uuid()

    def extract_uuid(self) -> str:
        """Extracts the KnowUnity ID from the given URL."""
        knowunity_uuid = re.search(self.UUID_REGEX, self.url)
        return knowunity_uuid.group() if knowunity_uuid else None

    def get_data(self) -> Dict:
        """Retrieves KnowUnity data from the API."""
        try:
            response = requests.get(self.API_ENDPOINT + self.uuid)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while retrieving KnowUnity data: {e}")
            return None

    def download_pdf(self):
        """Downloads KnowUnity PDF files."""
        data = self.get_data()
        if not data:
            return

        know_title = data["title"]
        know_content = data["contents"]
        know_content_urls = [content["contentUrl"] for content in know_content]
        know_page_counts = [content["pageCount"] for content in know_content]

        logging.debug(f"Title: {know_title}")
        logging.debug(f"Content URLs: {know_content_urls}")
        logging.debug(f"Page counts: {know_page_counts}")

        downloaded_files = []
        logging.info(f"Trying to download {len(know_content_urls)} PDF files...")
        for counter, know_content_url in enumerate(know_content_urls, start=1):
            try:
                content = requests.get(know_content_url)
                content.raise_for_status()
            except requests.exceptions.RequestException as e:
                logging.error(f"Failed to download {know_title}: {e}")
                continue

            filename = (
                f"{know_title}.pdf"
                if len(know_content_urls) == 1
                else f"{know_title}_{counter}.pdf"
                if counter > 0
                else f"{know_title}.pdf"
            )
            try:
                with open(filename, "wb") as file:
                    file.write(content.content)
            except IOError as e:
                logging.error(f"Failed to write {filename} to disk: {e}")
                continue

            downloaded_files.append(filename)
            logging.info(f"Successfully downloaded {know_title} to {filename}")

        if len(downloaded_files) == len(know_content_urls):
            logging.info(f"Successfully downloaded {len(downloaded_files)} PDF files")
        else:
            logging.error(
                f"Failed to download {len(know_content_urls) - len(downloaded_files)} PDF files"
            )


def main():
    url = input("Enter KnowUnity URL: ")
    knowunity = KnowUnity(url)
    knowunity.download_pdf()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
