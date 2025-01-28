import os
from lxml.html import fromstring
import requests
from tqdm import tqdm
import time

def read_book_urls(file_path="books.txt"):
    with open(file_path, "r") as file:
        return [line.strip() for line in file if line.strip()]

def sanitize_for_directory_name(name):
    # Replace invalid characters with underscores
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip().replace(' ', '_')

# Main function to download books
def download_book(book_url):
    url = book_url + "/files/mobile/"

    # Get book title
    try:
        response = requests.get(book_url)
        tree = fromstring(response.content)
        title = tree.findtext('.//title')
        if not title:
            title = "Unknown_Book"
    except Exception as e:
        print(f"Error fetching title from {book_url}: {e}")
        return

    title = sanitize_for_directory_name(title)
    directory_path = os.path.join(".", title)

    # Create directory if it does not exist
    os.makedirs(directory_path, exist_ok=True)

    i = 1
    pbar = tqdm()

    while True:
        filename = os.path.join(directory_path, f"{i}.jpg")

        if os.path.exists(filename):
            pbar.update(1)  # Increment progress if file exists
        else:
            try:
                myfile = requests.get(url + str(i) + ".jpg")
                if myfile.status_code == 200:
                    with open(filename, 'wb') as file:
                        file.write(myfile.content)
                    pbar.update(1)
                else:
                    break  # Stop if no more images exist
            except Exception as e:
                print(f"Connection error for file {i}: {e}")
                time.sleep(1)
                print(f"Retrying file {i}")
                continue

        i += 1

    pbar.close()
    print(f"Download completed for {title}")

# Read books and download each
if __name__ == "__main__":
    book_urls = read_book_urls()
    for book in book_urls:
        download_book(book)