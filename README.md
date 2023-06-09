# Knowunity PDF Downloader

This is a Python application for downloading PDFs from Knowunity. Tested on Windows 11 with Python 3.7.9 installed.

## Requirements

- Python 3.7
- PyQt5
- requests
- re

## Installation

1. Clone the repository.
2. Install the required packages using pip: `pip install -r requirements.txt`.

## Usage

### GUI
1. Click on the post you want to download.
2. Click Share and copy the URL.
3. Or search on https://knowunity.de/knows and copy the URL.
4. Run the application: `python maingui.py`.
5. Enter the URL of the post.
6. Select an output directory.
7. Click the "Download" button.

### CLI
1. Run the application: `python main.py`.
2. Paste your link in the terminal.
3. Read the logging information and wait for the finish message.

## Features

- Downloads PDFs from a Knowunity link.
- Fetches information from the KnowUnity API.
- Supports posts with multiple attached files.
- Saves PDFs to a specified output directory.
- GUI built with PyQt5.
- CLI interface also available.

## Disclaimer

Please note that web scraping and downloading content from a website without the owner's permission may be illegal in certain situations. However, after reviewing the TOS for Knowunity, I did not find any explicit prohibitions against these actions. Additionally, the code does not include any external API keys, authentication mechanisms, nor does it bypass any security measures. It only uses publicly available information.
Read the TOS here: https://knowunity.de/legal/tos

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
