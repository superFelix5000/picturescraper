import os
import urllib
import argparse
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

parser = argparse.ArgumentParser(
    prog = 'scraper',
    description = 'scrapes the images from a certain homepage')
parser.add_argument("--url", required=True, help="url of the homepage to scrape")
args = vars(parser.parse_args())
parsedBaseUrl = urlparse(args['url'])

def download_images(url, visited):
    # Fetch the HTML of the website
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all images on the website
    for img in soup.find_all('img'):
        img_url = img.get('src')
        if not img_url or not (img_url.endswith('jpg') or img_url.endswith('JPG')):
            continue
        
        # Construct full URL using urljoin
        img_url = urljoin(url, img_url)
        
        # Download the image
        img_data = requests.get(img_url).content
        # parse the image url, get only the path out of it, check if it exists and if not create the folder structure
        parsedImageUrl = urlparse(os.path.dirname(img_url))
        path = parsedImageUrl.path    
        if (path):
            # path = os.path.relpath(path)
            path = os.path.join('images', path[1:])
            if (not os.path.exists(path)):
                os.makedirs(path)
        else:
            path = 'images'
        filename = os.path.join(path, os.path.basename(img_url))
        # only create the file if it doesn't exist yet
        if not os.path.isfile(filename):
            with open(filename, 'wb') as f:
                f.write(img_data)
                print(f"Downloaded {img_url} to {filename}")
    
    # Follow all links on the website
    for link in soup.find_all('a'):
        link_url = link.get('href')
        if (not link_url or link_url.startswith('mailto')) or not (parsedBaseUrl.netloc in link_url) or (link_url.endswith('.pdf')):
            continue
        
        # Construct full URL using urljoin
        link_url = urljoin(url, link_url)

        # Check if the link URL is already visited
        if link_url not in visited:
            print(link_url)
            visited.add(link_url)
            # Recursively follow the link
            download_images(link_url, visited)

visited = set()
# Create the images directory if it doesn't exist
if not os.path.exists('images'):
    os.makedirs('images')

# Start the image download at the website's root
download_images(args['url'], visited)
