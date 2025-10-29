import os
import re
import tkinter as tk
from tkinter import messagebox, ttk
from bs4 import BeautifulSoup
import requests
import threading
from functools import partial

class LinkInput:
    def __init__(self, root):
        self.root = root
        self.link_entries = []
        self.name_labels = []
        self.progress_bars = []
        self.download_status = []
        self.is_downloading = False
        
        # Configurar estilo
        self.root.configure(bg='#2b2b2b')
        
        # Frame principal
        self.main_frame = tk.Frame(root, bg='#2b2b2b')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top frame com título e botão de download
        self.top_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = tk.Label(self.top_frame, 
                                    text="🎵 Spotify Downloader", 
                                    font=('Arial', 16, 'bold'),
                                    bg='#2b2b2b', 
                                    fg='#1DB954')
        self.title_label.pack(side=tk.LEFT)
        
        self.download_button = tk.Button(self.top_frame, 
                                        text="⬇️ Baixar Tudo", 
                                        command=self.download_from_gui,
                                        bg='#1DB954',
                                        fg='white',
                                        font=('Arial', 10, 'bold'),
                                        padx=20,
                                        pady=5,
                                        cursor='hand2',
                                        relief=tk.FLAT)
        self.download_button.pack(side=tk.RIGHT)
        
        # Label de controles
        self.control_label = tk.Label(self.main_frame, 
                                      text="Adicionar Links", 
                                      font=('Arial', 11, 'bold'),
                                      bg='#2b2b2b', 
                                      fg='#ffffff')
        self.control_label.pack(pady=(10, 5))
        
        # Frame dos botões
        self.button_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.button_frame.pack(pady=5)
        
        self.add_button = tk.Button(self.button_frame, 
                                    text="➕ Adicionar Link", 
                                    command=self.add_link,
                                    bg='#4CAF50',
                                    fg='white',
                                    font=('Arial', 10, 'bold'),
                                    padx=15,
                                    pady=8,
                                    cursor='hand2',
                                    relief=tk.FLAT)
        self.add_button.pack(side=tk.LEFT, padx=5)
        
        self.remove_button = tk.Button(self.button_frame, 
                                       text="➖ Remover Link", 
                                       command=self.remove_link,
                                       bg='#F44336',
                                       fg='white',
                                       font=('Arial', 10, 'bold'),
                                       padx=15,
                                       pady=8,
                                       cursor='hand2',
                                       relief=tk.FLAT,
                                       state='disabled')
        self.remove_button.pack(side=tk.LEFT, padx=5)
        
        # Frame para scroll
        self.scroll_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para scroll
        self.canvas = tk.Canvas(self.scroll_frame, bg='#2b2b2b', highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.scroll_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg='#2b2b2b')
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Adicionar primeiro entry
        self.add_link()
        
        # Barra de progresso geral
        self.overall_progress_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.overall_progress_frame.pack(fill=tk.X, pady=10)
        
        self.overall_progress_label = tk.Label(self.overall_progress_frame,
                                               text="Progresso Geral: 0%",
                                               font=('Arial', 10),
                                               bg='#2b2b2b',
                                               fg='#ffffff')
        self.overall_progress_label.pack()
        
        self.overall_progress = ttk.Progressbar(self.overall_progress_frame,
                                               mode='determinate',
                                               length=500)
        self.overall_progress.pack(fill=tk.X)

    def add_link(self):
        entry_frame = tk.Frame(self.scrollable_frame, bg='#2b2b2b')
        entry_frame.pack(fill=tk.X, pady=5)
        
        entry = tk.Entry(entry_frame, 
                        width=60,
                        font=('Arial', 9),
                        bg='#404040',
                        fg='white',
                        insertbackground='white',
                        relief=tk.FLAT,
                        bd=5)
        entry.pack(side=tk.LEFT, padx=(0, 10), ipady=8, fill=tk.X, expand=True)
        
        # Label para mostrar o nome da playlist/música
        name_label = tk.Label(entry_frame,
                             text="",
                             font=('Arial', 8, 'italic'),
                             bg='#2b2b2b',
                             fg='#888888',
                             wraplength=200)
        name_label.pack(side=tk.RIGHT)
        
        # Barra de progresso individual
        progress_frame = tk.Frame(self.scrollable_frame, bg='#2b2b2b')
        progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        progress_bar = ttk.Progressbar(progress_frame,
                                       mode='indeterminate',
                                       length=500)
        progress_bar.pack(fill=tk.X)
        
        entry.bind('<KeyRelease>', lambda e: self.update_name_label(entry, name_label))
        
        self.link_entries.append(entry)
        self.name_labels.append(name_label)
        self.progress_bars.append(progress_bar)
        self.download_status.append(False)
        
        self.update_remove_button_state()

    def remove_link(self):
        if self.link_entries and len(self.link_entries) > 1:
            entry = self.link_entries.pop()
            name_label = self.name_labels.pop()
            progress_bar = self.progress_bars.pop()
            status = self.download_status.pop()
            
            # Encontrar e destruir o frame pai
            parent_frame = entry.master
            progress_frame = progress_bar.master
            
            entry.destroy()
            name_label.destroy()
            progress_bar.destroy()
            parent_frame.destroy()
            progress_frame.destroy()
            
            self.update_remove_button_state()

    def update_remove_button_state(self):
        if len(self.link_entries) > 1:
            self.remove_button.config(state='normal')
        else:
            self.remove_button.config(state='disabled')

    def update_name_label(self, entry, name_label):
        link = entry.get().strip()
        if link and re.match(r'https?://', link):
            # Atualizar o nome em thread separada para não travar a UI
            threading.Thread(target=self.fetch_name, args=(link, name_label), daemon=True).start()
        else:
            name_label.config(text="")

    def fetch_name(self, link, name_label):
        try:
            response = requests.get(link, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title else "Carregando..."
            
            # Limpar o título
            title = title.split(',')[0].strip()
            if len(title) > 40:
                title = title[:40] + "..."
            
            name_label.config(text=title)
        except:
            name_label.config(text="Erro ao carregar")

    def download_music(self, index, link, progress_bar):
        try:
            # Caminho absoluto para a pasta de músicas na raiz do projeto
            musicas_dir = os.path.join(current_path, "musicas")
            
            if not os.path.exists(musicas_dir):
                os.makedirs(musicas_dir)

            response = requests.get(link)
            soup = BeautifulSoup(response.text, 'html.parser')
            album_name = soup.title.string.split(',')[0].strip()

            sanitized_album_name = self.sanitize_filename(album_name)
            folder_name = os.path.join(musicas_dir, sanitized_album_name)

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            # Mudar para a pasta do álbum e baixar
            original_dir = os.getcwd()
            os.chdir(folder_name)
            os.system(f'python3 -m spotdl {link}')
            os.chdir(original_dir)
            
            self.download_status[index] = True
            progress_bar.config(mode='determinate', value=100)
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao baixar: {str(e)}")
            self.download_status[index] = False

    def sanitize_filename(self, name):
        return re.sub(r'[<>:"/\\|?*]', '', name)

    def download_from_gui(self):
        if self.is_downloading:
            messagebox.showwarning("Aviso", "Download já em andamento!")
            return
            
        # Verificar se há links válidos
        valid_links = []
        for i, entry in enumerate(self.link_entries):
            link = entry.get().strip()
            if link and re.match(r'https?://', link):
                valid_links.append((i, link))
        
        if not valid_links:
            messagebox.showerror("Erro", "Por favor, insira pelo menos um link válido!")
            return
        
        # Desabilitar botão durante download
        self.is_downloading = True
        self.download_button.config(state='disabled')
        
        # Resetar status
        for i in range(len(self.download_status)):
            self.download_status[i] = False
            self.progress_bars[i].config(mode='indeterminate', value=0)
        
        # Barra de progresso geral
        self.overall_progress.config(maximum=len(valid_links), value=0)
        self.overall_progress_label.config(text=f"Progresso Geral: 0/{len(valid_links)}")
        
        # Download em thread separada
        threading.Thread(target=self.download_all, args=(valid_links,), daemon=True).start()

    def download_all(self, valid_links):
        for idx, (index, link) in enumerate(valid_links):
            progress_bar = self.progress_bars[index]
            progress_bar.config(mode='indeterminate')
            progress_bar.start()
            
            self.download_music(index, link, progress_bar)
            
            progress_bar.stop()
            progress_bar.config(mode='determinate', value=100)
            
            # Atualizar progresso geral
            self.overall_progress.config(value=idx + 1)
            self.overall_progress_label.config(
                text=f"Progresso Geral: {idx + 1}/{len(valid_links)}"
            )
        
        self.is_downloading = False
        self.root.after(0, lambda: self.download_button.config(state='normal'))
        
        self.root.after(0, lambda: messagebox.showinfo(
            "Download Concluído", 
            "Downloads das músicas concluídos!"
        ))

current_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
