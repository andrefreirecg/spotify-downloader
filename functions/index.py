import tkinter as tk
from classes import LinkInput

root = tk.Tk()
root.title("Spotify - Download Musicas - Playlist, musicas, albuns...")
root.geometry("800x600")
root.resizable(True, True)

link_input = LinkInput(root)

root.mainloop()
