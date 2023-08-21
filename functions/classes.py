import os
import re
import tkinter as tk
from tkinter import messagebox
from bs4 import BeautifulSoup
import requests

class LinkInput:
    def __init__(self, root):
        self.root = root
        self.link_entries = []

        self.control_label = tk.Label(root, text="Controle de linhas")
        self.control_label.grid(row=0, column=0, columnspan=2)

        self.add_button = tk.Button(root, text="+", command=self.add_link)
        self.add_button.grid(row=1, column=0)

        self.remove_button = tk.Button(root, text="-", command=self.remove_link)
        self.remove_button.grid(row=1, column=1)
        self.remove_button.config(state='disabled')

        entry = tk.Entry(self.root, width=50)
        entry.grid(row=len(self.link_entries) +  3, column=0, columnspan=2, sticky='w')
        self.link_entries.append(entry)

        self.download_button = tk.Button(root, text="Baixar Tudo", command=self.download_from_gui)
        self.download_button.grid(row=2, column=0, columnspan=2)

    def add_link(self):
        entry = tk.Entry(self.root, width=50)
        entry.grid(row=len(self.link_entries) + 3, column=0, columnspan=2, sticky='w')
        self.link_entries.append(entry)
        self.update_remove_button_state()

    def remove_link(self):
        if self.link_entries:
            entry = self.link_entries.pop()
            entry.destroy()
            self.update_remove_button_state()

    def update_remove_button_state(self):
        if len(self.link_entries) > 1:
            self.remove_button.config(state='normal')
        else:
            self.remove_button.config(state='disabled')

    def download_music(self, link):
        if not os.path.exists("musicas"):
            os.mkdir("musicas")

        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        album_name = soup.title.string.split(',')[0].strip()

        sanitized_album_name = self.sanitize_filename(album_name)
        folder_name = f"musicas/{sanitized_album_name}/"

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        os.chdir(folder_name)

        os.system(f'python3 -m spotdl {link}')
        os.chdir(current_path)

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', '', name)

    def download_from_gui(self):
        for entry in self.link_entries:
            link = entry.get().strip()
            if re.match(r'https?://', link):
                self.download_music(link)
            else:
                messagebox.showerror("Erro de URL", f"URL inválida: {link}")

        messagebox.showinfo("Download Concluído", "Downloads das músicas concluídos.")

current_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
