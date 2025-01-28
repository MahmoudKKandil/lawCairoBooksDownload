import os
import re
import requests
import time
from lxml.html import fromstring
from tqdm import tqdm
from PIL import Image  # For PDF conversion

# Read book URLs from books.txt
def read_book_urls(file_path="books.txt"):
    with open(file_path, "r") as file:
        urls = [line.strip() for line in file if line.strip()]
    return [sanitize_url(url) for url in urls]

# Function to trim extra parts from the URL
def sanitize_url(url):
    match = re.match(r"(https://law\.cu\.edu\.eg/books/.+?/\d+)", url)
    return match.group(1) if match else None

# Function to sanitize directory names
def sanitize_for_directory_name(name):
    invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        name = name.replace(char, '_')
    return name.strip().replace(' ', '_')

# Function to convert images to a PDF
def images_to_pdf(directory_path, book_title):
    pdf_path = os.path.join(directory_path, f"{book_title}.pdf")

    if os.path.exists(pdf_path):
        print(f"PDF already exists: {pdf_path}, skipping conversion.")
        return

    image_files = sorted(
        [f for f in os.listdir(directory_path) if f.endswith(".jpg")],
        key=lambda x: int(x.split('.')[0])  # Sort numerically (1.jpg, 2.jpg, etc.)
    )

    if not image_files:
        print(f"No images found in {directory_path}, skipping PDF conversion.")
        return

    images = [Image.open(os.path.join(directory_path, img)).convert("RGB") for img in image_files]

    # Save images as PDF
    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print(f"PDF created: {pdf_path}")

# Main function to download books
def download_book(book_url):
    if not book_url:
        print("Invalid URL, skipping...")
        return

    url = book_url + "/files/mobile/"

    # Get book title
    try:
        response = requests.get(book_url)
        tree = fromstring(response.content)
        title = tree.findtext('.//title') or "Unknown_Book"
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

    # Convert downloaded images to PDF
    images_to_pdf(directory_path, title)

# Read books and download each
if __name__ == "__main__":
    book_urls = read_book_urls()
    for book in book_urls:
        if book:
            download_book(book)
