import os
import re
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from bs4 import BeautifulSoup
import requests
import threading
from functools import partial
import subprocess
import json

class LinkInput:
    def __init__(self, root):
        self.root = root
        self.link_entries = []
        self.name_labels = []
        self.progress_bars = []
        self.progress_labels = []
        self.download_status = []
        self.is_downloading = False
        self.cancel_download = False
        self.total_tracks = []
        self.current_track_info = []
        
        # Configurar estilo
        self.root.configure(bg='#2b2b2b')
        
        # Caminho de salvamento padrão
        self.download_path = current_path
        
        # Frame principal
        self.main_frame = tk.Frame(root, bg='#2b2b2b')
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Mostrar diálogo para escolher pasta de download (depois de criar os widgets)
        self.root.after(100, self.show_download_path_dialog)
        
        # Top frame com título e botão de download
        self.top_frame = tk.Frame(self.main_frame, bg='#2b2b2b')
        self.top_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = tk.Label(self.top_frame, 
                                    text="🎵 Spotify Downloader", 
                                    font=('Arial', 16, 'bold'),
                                    bg='#2b2b2b', 
                                    fg='#1DB954')
        self.title_label.pack(side=tk.LEFT)
        
        # Botão para mudar pasta de download
        self.path_button = tk.Button(self.top_frame, 
                                     text="📁 Alterar Pasta", 
                                     command=self.show_download_path_dialog,
                                     bg='#555555',
                                     fg='white',
                                     font=('Arial', 8),
                                     padx=10,
                                     pady=3,
                                     cursor='hand2',
                                     relief=tk.FLAT)
        self.path_button.pack(side=tk.LEFT, padx=(10, 0))
        
        # Label mostrando pasta atual
        self.path_label = tk.Label(self.top_frame,
                                   text="",
                                   font=('Arial', 7),
                                   bg='#2b2b2b',
                                   fg='#999999',
                                   wraplength=200)
        self.path_label.pack(side=tk.LEFT, padx=5)
        
        # Botão de download
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
        self.download_button.pack(side=tk.RIGHT, padx=5)
        
        # Botão de cancelar
        self.cancel_button = tk.Button(self.top_frame, 
                                       text="❌ Cancelar", 
                                       command=self.cancel_download_all,
                                       bg='#F44336',
                                       fg='white',
                                       font=('Arial', 10, 'bold'),
                                       padx=20,
                                       pady=5,
                                       cursor='hand2',
                                       relief=tk.FLAT,
                                       state='disabled')
        self.cancel_button.pack(side=tk.RIGHT)
        
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
        
        # Atualizar label da pasta inicialmente
        if self.download_path == current_path:
            self.path_label.config(text="Salvando em: ./musicas (padrão)")
        else:
            self.path_label.config(text=f"Salvando em: {os.path.basename(self.download_path)}")

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
        
        # Label de progresso individual
        progress_label = tk.Label(progress_frame,
                                  text="",
                                  font=('Arial', 8),
                                  bg='#2b2b2b',
                                  fg='#ffffff')
        progress_label.pack(pady=(0, 5))
        
        entry.bind('<KeyRelease>', lambda e: self.update_name_label(entry, name_label))
        
        self.link_entries.append(entry)
        self.name_labels.append(name_label)
        self.progress_bars.append(progress_bar)
        self.progress_labels.append(progress_label)
        self.download_status.append(False)
        self.total_tracks.append(0)
        self.current_track_info.append("")
        
        self.update_remove_button_state()

    def remove_link(self):
        if self.link_entries and len(self.link_entries) > 1:
            entry = self.link_entries.pop()
            name_label = self.name_labels.pop()
            progress_bar = self.progress_bars.pop()
            progress_label = self.progress_labels.pop()
            status = self.download_status.pop()
            total_tracks = self.total_tracks.pop()
            track_info = self.current_track_info.pop()
            
            # Encontrar e destruir o frame pai
            parent_frame = entry.master
            progress_frame = progress_bar.master
            
            entry.destroy()
            name_label.destroy()
            progress_bar.destroy()
            progress_label.destroy()
            parent_frame.destroy()
            progress_frame.destroy()
            
            self.update_remove_button_state()

    def update_remove_button_state(self):
        if len(self.link_entries) > 1:
            self.remove_button.config(state='normal')
        else:
            self.remove_button.config(state='disabled')
    
    def show_download_path_dialog(self):
        """Mostra diálogo para escolher pasta de download"""
        result = messagebox.askyesno(
            "🎵 Spotify Downloader",
            "Deseja escolher uma pasta personalizada para salvar as músicas?\n\n" +
            f"📁 Pasta padrão: {os.path.join(current_path, 'musicas')}\n\n" +
            "Clique em 'Sim' para escolher outra pasta ou 'Não' para usar a padrão.",
            icon='question'
        )
        
        if result:
            # Pergunta se quer escolher uma pasta específica ou o padrão
            folder = filedialog.askdirectory(
                title="Selecionar Pasta para Salvar Músicas",
                initialdir=current_path
            )
            if folder:
                self.download_path = folder
                self.path_label.config(text=f"Salvando em: {os.path.basename(folder)}")
                messagebox.showinfo("✅ Pasta Alterada", f"Músicas serão salvas em:\n{folder}")
            else:
                # Usuário cancelou, usa o padrão
                self.download_path = current_path
                self.path_label.config(text="Salvando em: ./musicas (padrão)")
        else:
            # Usa a pasta padrão
            self.download_path = current_path
            self.path_label.config(text="Salvando em: ./musicas (padrão)")

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
    
    def is_playlist(self, link):
        """Verifica se o link é uma playlist do Spotify"""
        return 'playlist' in link.lower()
    
    def get_playlist_info(self, link):
        """Obtém informações da playlist usando spotdl"""
        try:
            # Usar spotdl para obter informações da playlist
            result = subprocess.run(
                ['python3', '-m', 'spotdl', '--save-file', '-', link],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0 and result.stdout:
                # Contar linhas (cada linha é uma música)
                tracks = result.stdout.strip().split('\n')
                return len([t for t in tracks if t.strip()])
            return 0
        except Exception as e:
            print(f"Erro ao obter info da playlist: {e}")
            return 0
    
    def cancel_download_all(self):
        """Cancela o download em andamento"""
        self.cancel_download = True
        self.cancel_button.config(state='disabled')
        messagebox.showinfo("Cancelado", "Cancelando downloads...")

    def download_music(self, index, link, progress_bar, progress_label):
        try:
            if self.cancel_download:
                return
            
            # Caminho para a pasta de músicas (usa o escolhido pelo usuário ou padrão)
            if self.download_path == current_path:
                musicas_dir = os.path.join(current_path, "musicas")
            else:
                musicas_dir = os.path.join(self.download_path, "musicas")
            
            if not os.path.exists(musicas_dir):
                os.makedirs(musicas_dir)

            response = requests.get(link, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            album_name = soup.title.string.split(',')[0].strip() if soup.title else "Desconhecido"

            sanitized_album_name = self.sanitize_filename(album_name)
            folder_name = os.path.join(musicas_dir, sanitized_album_name)

            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            # Verificar se é playlist
            is_playlist = self.is_playlist(link)
            
            if is_playlist:
                # Obter total de músicas
                total = self.total_tracks[index]
                if total == 0:
                    total = self.get_playlist_info(link)
                    self.total_tracks[index] = total
                
                # Baixar com progresso
                original_dir = os.getcwd()
                os.chdir(folder_name)
                
                # Usar subprocess para capturar a saída
                process = subprocess.Popen(
                    ['python3', '-m', 'spotdl', link],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                downloaded = 0
                for line in process.stdout:
                    if self.cancel_download:
                        process.terminate()
                        break
                    if 'Downloading' in line or 'Downloaded' in line:
                        downloaded += 1
                        progress = int((downloaded / total) * 100) if total > 0 else 0
                        progress_bar.config(mode='determinate', value=progress)
                        self.current_track_info[index] = f"Baixando: {line.strip()}"
                        self.root.after(0, lambda idx=index: progress_label.config(
                            text=f"{self.current_track_info[idx] if idx < len(self.current_track_info) else ''}"
                        ))
                
                process.wait()
                os.chdir(original_dir)
                
                if not self.cancel_download:
                    self.download_status[index] = True
                    progress_bar.config(mode='determinate', value=100)
                    progress_label.config(text="✓ Download concluído!")
            else:
                # Não é playlist, usar método simples
                original_dir = os.getcwd()
                os.chdir(folder_name)
                os.system(f'python3 -m spotdl {link}')
                os.chdir(original_dir)
                
                if not self.cancel_download:
                    self.download_status[index] = True
                    progress_bar.config(mode='determinate', value=100)
                    progress_label.config(text="✓ Download concluído!")
            
        except Exception as e:
            if not self.cancel_download:
                messagebox.showerror("Erro", f"Erro ao baixar: {str(e)}")
            self.download_status[index] = False
            progress_label.config(text=f"✗ Erro: {str(e)}")

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
        self.cancel_download = False
        self.download_button.config(state='disabled')
        self.cancel_button.config(state='normal')
        
        # Resetar status
        for i in range(len(self.download_status)):
            self.download_status[i] = False
            self.progress_bars[i].config(mode='determinate', value=0, maximum=100)
            self.progress_labels[i].config(text="")
            self.current_track_info[i] = ""
            self.total_tracks[i] = 0
        
        # Barra de progresso geral
        self.overall_progress.config(maximum=len(valid_links), value=0)
        self.overall_progress_label.config(text=f"Progresso Geral: 0/{len(valid_links)}")
        
        # Download em thread separada
        threading.Thread(target=self.download_all, args=(valid_links,), daemon=True).start()

    def download_all(self, valid_links):
        for idx, (index, link) in enumerate(valid_links):
            if self.cancel_download:
                self.progress_labels[index].config(text="✗ Cancelado")
                break
                
            progress_bar = self.progress_bars[index]
            progress_label = self.progress_labels[index]
            
            # Mostrar que está iniciando
            self.root.after(0, lambda idx=index: self.progress_labels[idx].config(
                text="Iniciando download..."
            ))
            
            # Se for playlist, obter info primeiro
            if self.is_playlist(link):
                self.root.after(0, lambda idx=index: self.progress_labels[idx].config(
                    text="Contando músicas da playlist..."
                ))
                total = self.get_playlist_info(link)
                self.total_tracks[index] = total
                self.root.after(0, lambda idx=index, t=total: self.progress_labels[idx].config(
                    text=f"Total de músicas: {t}"
                ))
            
            self.download_music(index, link, progress_bar, progress_label)
            
            # Atualizar progresso geral
            if not self.cancel_download:
                self.overall_progress.config(value=idx + 1)
                self.overall_progress_label.config(
                    text=f"Progresso Geral: {idx + 1}/{len(valid_links)}"
                )
        
        self.is_downloading = False
        self.root.after(0, lambda: self.download_button.config(state='normal'))
        self.root.after(0, lambda: self.cancel_button.config(state='disabled'))
        
        if not self.cancel_download:
            self.root.after(0, lambda: messagebox.showinfo(
                "Download Concluído", 
                "Downloads das músicas concluídos!"
            ))
        else:
            self.root.after(0, lambda: messagebox.showinfo(
                "Download Cancelado", 
                "Downloads foram cancelados."
            ))

current_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
