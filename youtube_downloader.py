import os
import threading
import yt_dlp
from tkinter import Tk, Label, Entry, Button, filedialog, ttk, Text, DISABLED, NORMAL, END

def download_video():
    url = url_entry.get()
    output_dir = filedialog.askdirectory(title="Select Download Directory")
    
    if not output_dir:
        return
    
    download_button.config(state=DISABLED)
    log_text.config(state=NORMAL)
    log_text.delete('1.0', END)
    log_text.insert(END, "Download started...\n")
    log_text.config(state=DISABLED)
    
    download_thread = threading.Thread(target=perform_download, args=(url, output_dir))
    download_thread.start()

def perform_download(url, output_dir):
    video_opts = {
        'format': 'bestvideo+bestaudio',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'progress_hooks': [update_progress],
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4'
        }],
    }

    audio_opts = {
        'format': 'bestaudio',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'progress_hooks': [update_progress],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
    }

    try:
        # Download video
        log("Starting video download...")
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            ydl.download([url])
        log("Video download completed.")

        # Download audio
        log("Starting audio download...")
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            ydl.download([url])
        log("Audio download completed.")

        status_label.config(text="Download completed!", fg="green")
    except Exception as e:
        status_label.config(text=f"Error: {e}", fg="red")
    finally:
        download_button.config(state=NORMAL)

def update_progress(d):
    if d['status'] == 'downloading':
        percent = float(d['_percent_str'].strip()[:-1])
        progress_bar['value'] = percent
        progress_label.config(text=f"{percent:.2f}%")
        log(f"Downloading... {percent:.2f}%")
        root.update_idletasks()
    elif d['status'] == 'finished':
        progress_bar['value'] = 100
        progress_label.config(text="100%")
        log("Download finished. Converting...")

def log(message):
    log_text.config(state=NORMAL)
    log_text.insert(END, message + "\n")
    log_text.config(state=DISABLED)
    log_text.see(END)
    root.update_idletasks()

def paste_clipboard():
    try:
        clipboard_content = root.clipboard_get()
        url_entry.delete(0, 'end')
        url_entry.insert(0, clipboard_content)
    except Exception:
        status_label.config(text="Failed to paste from clipboard", fg="red")

# GUI setup
root = Tk()
root.title("YouTube Downloader")

url_label = Label(root, text="YouTube URL:")
url_label.grid(row=0, column=0, padx=10, pady=10)

url_entry = Entry(root, width=50)
url_entry.grid(row=0, column=1, padx=10, pady=10)

paste_button = Button(root, text="Paste", command=paste_clipboard)
paste_button.grid(row=0, column=2, padx=10, pady=10)

download_button = Button(root, text="Download", command=download_video)
download_button.grid(row=1, column=0, columnspan=3, padx=10, pady=10)

progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
progress_bar.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

progress_label = Label(root, text="0%")
progress_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

log_text = Text(root, height=10, width=70, state=DISABLED)
log_text.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

status_label = Label(root, text="", fg="green")
status_label.grid(row=5, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()
