import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Telegram Bot API credentials
BOT_TOKEN = '7398616298:AAHk5Zp50W_Jzd6jQ_q9ORwe3XIJdPV7RSk'
CHAT_ID = '5838829750'

# Function to send a file to Telegram and delete it after successful upload
def send_file_to_telegram(file_path, bot_token, chat_id):
    try:
        url = f'https://api.telegram.org/bot{bot_token}/sendDocument'
        with open(file_path, 'rb') as file:
            payload = {'chat_id': chat_id}
            files = {'document': file}
            response = requests.post(url, data=payload, files=files)
        if response.status_code == 200:
            print(f"Successfully sent {file_path} to Telegram.")
            os.remove(file_path)  # Delete the file after successful upload
            print(f"Deleted {file_path}.")
        else:
            print(f"Failed to send {file_path}. Response: {response.text}")
    except Exception as e:
        print(f"Error sending file: {e}")

# Function to download a webpage with its images and save it as .html
def download_webpage_with_images(url, folder_name):
    try:
        # Create a folder for the webpage if it doesn't exist
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        # Fetch the webpage content
        response = requests.get(url)
        response.raise_for_status()  # Check for HTTP request errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Save the HTML content to a file
        html_file_path = os.path.join(folder_name, 'index.html')
        with open(html_file_path, 'w', encoding='utf-8') as file:
            file.write(soup.prettify())

        print(f"HTML file saved as {html_file_path}")

        # Download images from the webpage
        download_images(soup, url, folder_name)

        # Send the HTML file and images to Telegram
        send_file_to_telegram(html_file_path, BOT_TOKEN, CHAT_ID)
        for root, _, files in os.walk(folder_name):
            for file in files:
                file_path = os.path.join(root, file)
                send_file_to_telegram(file_path, BOT_TOKEN, CHAT_ID)

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except Exception as e:
        print(f"Error: {e}")

# Function to download all images in the webpage and save them locally
def download_images(soup, page_url, folder_name):
    # Find all image tags in the HTML
    images = soup.find_all('img')

    for img in images:
        # Get the image source URL
        img_url = img.get('src')
        if not img_url:
            continue  # Skip if no src attribute

        # Handle relative URLs by converting them to absolute URLs
        img_url = urljoin(page_url, img_url)

        # Extract the image file name
        img_name = os.path.basename(urlparse(img_url).path)
        if not img_name:
            continue  # Skip if no image name

        # Define the local path to save the image
        img_path = os.path.join(folder_name, img_name)

        # Download and save the image
        try:
            img_data = requests.get(img_url)
            img_data.raise_for_status()  # Check for HTTP request errors
            with open(img_path, 'wb') as f:
                f.write(img_data.content)
            print(f"Image saved: {img_path}")
        except requests.RequestException as e:
            print(f"Failed to download image {img_url}: {e}")
        except Exception as e:
            print(f"Error saving image {img_url}: {e}")

# URL of the webpage you want to download
url = 'https://www.erome.com/explore?page=1'

# Folder where the HTML and images will be saved
folder_name = 'downloaded_webpage'

# Download the webpage with its images and send files to Telegram
download_webpage_with_images(url, folder_name)
