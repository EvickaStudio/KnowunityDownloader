import json
import logging
import os
import re
from typing import List

import requests
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QCheckBox, QFileDialog, QHBoxLayout,
                             QLabel, QLineEdit, QMainWindow, QMessageBox,
                             QProgressBar, QPushButton, QVBoxLayout, QWidget)


class KnowUnityPDFLoader:
    """
    A class for loading PDF links from a KnowUnity page.
    """

    def __init__(self, url: str) -> None:
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "KnowUnityPDFLoader/1.0"})
        self.regex = r"https://content-eu-central-1\.knowunity\.com/CONTENT/([A-Za-z0-9_]+)(?:_COMPRESSED)?\.pdf"

    def get_pdf_links(self) -> List[str]:
        """
        Gets a list of PDF links from the KnowUnity page.
        """
        response = self.session.get(self.url)
        matches = re.findall(self.regex, response.text)
        return PDFLinkHandler(matches).remove_duplicates()


class PDFLinkHandler:
    """
    A class for handling PDF links.
    """

    def __init__(self, links: List[str]) -> None:
        self.links = links

    def remove_duplicates(self) -> List[str]:
        """
        Removes duplicate PDF links from the list.
        """
        return list(
            dict.fromkeys(
                [
                    f"https://content-eu-central-1.knowunity.com/CONTENT/{link}.pdf"
                    for link in self.links
                ]
            )
        )


class MainWindow(QMainWindow):
    """
    The main window of the application.
    """

    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("Knowunity PDF Downloader")

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        url_layout = QHBoxLayout()
        url_label = QLabel("URL:")
        url_layout.addWidget(url_label)
        self.url_edit = QLineEdit()
        url_layout.addWidget(self.url_edit)
        layout.addLayout(url_layout)

        output_layout = QHBoxLayout()
        output_label = QLabel("Output directory:")
        output_layout.addWidget(output_label)
        self.output_edit = QLineEdit()
        output_layout.addWidget(self.output_edit)
        output_button = QPushButton("Browse")
        output_button.clicked.connect(self.browse_output_dir)
        output_layout.addWidget(output_button)
        layout.addLayout(output_layout)

        self.dark_mode_checkbox = QCheckBox("Dark mode")
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_checkbox)

        download_button = QPushButton("Download")
        download_button.clicked.connect(self.download_pdfs)
        layout.addWidget(download_button)

        # Load last used output directory and dark mode state
        self.last_output_dir, self.dark_mode = self.load_config()
        if self.last_output_dir:
            self.output_edit.setText(self.last_output_dir)
        if self.dark_mode:
            self.dark_mode_checkbox.setChecked(True)
            self.toggle_dark_mode()

    def download_pdfs(self) -> None:
        """
        Downloads PDFs from the URL and saves them to the output directory.
        """
        url = self.url_edit.text()
        if not url:
            QMessageBox.warning(self, "Error", "Please enter a URL.")
            return

        # Check if URL matches expected pattern
        if not re.match(r"https://knowunity\.de/knows/.*", url):
            QMessageBox.warning(self, "Error", "Invalid URL.")
            return

        output_dir = self.output_edit.text()
        if not output_dir:
            QMessageBox.warning(self, "Error", "Please select an output directory.")
            return

        # Check if output directory exists
        if not os.path.exists(output_dir):
            QMessageBox.warning(self, "Error", "Output directory does not exist.")
            return

        try:
            loader = KnowUnityPDFLoader(url)
            pdf_links = loader.get_pdf_links()

            logging.info("Downloading PDFs...")
            for pdf_link in pdf_links:
                pdf_name = pdf_link.split("/")[-1].split("_")[0]
                pdf_path = os.path.join(output_dir, f"{pdf_name}.pdf")
                if os.path.exists(pdf_path):
                    continue
                response = requests.get(pdf_link, stream=True)
                with open(pdf_path, "wb") as f:
                    for data in response.iter_content(chunk_size=4096):
                        f.write(data)
            logging.info("Done.")

            # Save last used output directory
            self.save_config(output_dir, self.dark_mode)

            QMessageBox.information(self, "Success", "PDFs downloaded successfully.")
        except Exception as e:
            logging.exception(e)
            QMessageBox.critical(
                self, "Error", "An error occurred while downloading the PDFs."
            )

    def browse_output_dir(self) -> None:
        """
        Opens a file dialog to select the output directory.
        """
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        output_dir = QFileDialog.getExistingDirectory(
            self, "Select output directory", options=options
        )
        if output_dir:
            self.output_edit.setText(output_dir)

    def toggle_dark_mode(self) -> None:
        """
        Toggles dark mode and saves the state to the config file.
        """
        if self.dark_mode_checkbox.isChecked():
            self.setStyleSheet("background-color: #333; color: #fff;")
            self.dark_mode = True
        else:
            self.setStyleSheet("")
            self.dark_mode = False
        self.save_config(self.last_output_dir, self.dark_mode)

    def load_config(self) -> tuple:
        """
        Loads the last used output directory and dark mode state from a file.
        """
        try:
            with open("config.json", "r") as f:
                data = json.load(f)
                return data.get("last_output_dir"), data.get("dark_mode")
        except:
            return "", False

    def save_config(self, output_dir: str, dark_mode: bool) -> None:
        """
        Saves the last used output directory and dark mode state to a file.
        """
        data = {"last_output_dir": output_dir, "dark_mode": dark_mode}
        with open("config.json", "w") as f:
            json.dump(data, f)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
