import logging
import os
import re
import sys
from typing import Dict, List

import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QStatusBar,
                             QVBoxLayout, QWidget)


class KnowUnityGui(QMainWindow):
    API_ENDPOINT = "https://apiedge-eu-central-1.knowunity.com/knows/"
    UUID_REGEX = r"[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}"

    def __init__(self):
        super().__init__()

        # Set window title
        self.setWindowTitle("Knowloader v0.2")

        # Set up UI elements
        self.url_input = QLineEdit()
        self.output_dir_input = QLineEdit()
        self.output_dir_button = QPushButton("Choose Output Directory")
        self.download_button = QPushButton("Download")
        self.status_bar = QStatusBar()

        # Set up layouts
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("URL:"))
        url_layout.addWidget(self.url_input)

        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(QLabel("Output Directory:"))
        output_dir_layout.addWidget(self.output_dir_input)
        output_dir_layout.addWidget(self.output_dir_button)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.download_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(url_layout)
        main_layout.addLayout(output_dir_layout)
        main_layout.addLayout(button_layout)

        # Set up main widget
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # Set up status bar
        self.setStatusBar(self.status_bar)

        # Set up signals and slots
        self.output_dir_button.clicked.connect(self.select_output_dir)
        self.download_button.clicked.connect(self.download_pdf)

        self.load_settings()

    def select_output_dir(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select output directory", options=options
        )
        if output_dir:
            self.output_dir_input.setText(output_dir)
            self.save_settings()

    def download_pdf(self):
        url = self.url_input.text()
        output_dir = self.output_dir_input.text()

        if not url:
            self.status_bar.showMessage("Please enter a URL")
            return

        if not output_dir or not os.path.isdir(output_dir):
            self.status_bar.showMessage("Please choose a valid output directory")
            return

        knowunity = KnowUnity(url)
        if not knowunity.uuid:
            self.status_bar.showMessage("Invalid URL")
            return

        try:
            knowunity.download_pdf(output_dir)
            self.status_bar.showMessage("Download complete")
        except Exception as e:
            self.status_bar.showMessage(str(e))

    def save_settings(self):
        settings = {"output_dir": self.output_dir_input.text()}
        with open("settings.txt", "w") as f:
            for key, value in settings.items():
                f.write(f"{key}={value}\n")

    def load_settings(self):
        try:
            with open("settings.txt", "r") as f:
                settings = dict(line.strip().split("=") for line in f)
                self.output_dir_input.setText(settings.get("output_dir", ""))
        except FileNotFoundError:
            pass


class KnowUnity:
    def __init__(self, url: str):
        self.url = url
        self.uuid = self.extract_uuid()

    def extract_uuid(self) -> str:
        """Extracts the KnowUnity ID from the given URL."""
        knowunity_uuid = re.search(KnowUnityGui.UUID_REGEX, self.url)
        return knowunity_uuid.group() if knowunity_uuid else None

    def get_data(self) -> Dict:
        """Retrieves KnowUnity data from the API."""
        try:
            response = requests.get(KnowUnityGui.API_ENDPOINT + self.uuid)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Error occurred while retrieving KnowUnity data: {e}")
            return None

    def download_pdf(self, output_dir: str):
        """Downloads KnowUnity PDF files."""
        data = self.get_data()
        if not data:
            raise Exception("Failed to retrieve KnowUnity data")

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
            with open(f"{output_dir}/{filename}", "wb") as file:
                file.write(content.content)
            downloaded_files.append(filename)
            logging.info(f"Successfully downloaded {know_title} to {filename}")

        if len(downloaded_files) != len(know_content_urls):
            raise Exception("Failed to download all PDF files")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    app = QApplication(sys.argv)
    gui = KnowUnityGui()
    #app.setWindowIcon(QIcon("Knowunity.ico"))
    gui.show()

    sys.exit(app.exec_())