# Knowunity PDF Downloader

This is a Python application for downloading PDFs from Knowunity. Tested on Python 3.7.9

## Requirements

- Python 3.x
- PyQt5
- requests
- re

## Installation

1. Clone the repository.
2. Install the required packages using pip: `pip install -r requirements.txt`.

## Usage

1. Click on the post you want to download
2. Click Share and copy the URL.
3. Or search on https://knowunity.de/knows and copy the URL.
4. Run the application: `python main.py`.
5. Enter the URL of the post.
6. Select an output directory.
7. Click the "Download" button.

## Features

- Downloads PDFs from a Knowunity link.
- Supports posts with multiple attached files.
- Saves PDFs to a specified output directory.
- Dark mode available.
- GUI built with PyQt5.

## Disclaimer

Please note that web scraping and downloading content from a website without the owner's permission may be illegal in certain situations. However, after reviewing the TOS for Knowunity, I did not find any explicit prohibitions against these actions. Additionally, the code does not include any external API keys, authentication mechanisms, nor does it bypass any security measures. It only uses publicly available information.
Read the TOS her: https://knowunity.de/legal/tos

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
