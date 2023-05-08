import os, re, requests
from bs4 import BeautifulSoup

current_path = os.path.abspath(os.path.dirname(__file__))
links = [
    "https://open.spotify.com/playlist/0QYQbFTkVVj2DxYG3HEw15",
]

for link in links:
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    album_name = soup.title.string.split(',')[0].strip().replace('|', '-').replace(' ', '-')

    folder_name = f"{album_name}/"

    if not os.path.exists(folder_name):
        os.mkdir(folder_name)
    os.chdir(folder_name)

    os.system(f'python3 -m spotdl {link}')
    os.chdir(current_path)

