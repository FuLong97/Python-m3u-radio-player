from tkinter import *
from ttkbootstrap import *
from ttkbootstrap.style import Style
import ttkbootstrap as ttk
import vlc
from ttkbootstrap.constants import *
from ttkbootstrap.toast import ToastNotification
import requests
import threading

player = None

def play_radio():
    global player
    stream = selected_stream.get()
    player = vlc.MediaPlayer(stream)
    player.play()

def pause_radio():
    global player
    player.stop()

def change_volume(event):
    global player
    volume = int(volume_slider.get())
    if player:
        player.audio_set_volume(volume)
    volume_percentage = volume / 100  # Calculate volume percentage
    volume_label.configure(text="Volume: {:.0%}".format(volume_percentage))

def fetch_radio_metadata():
    stream_url = selected_stream.get()
    while True:
        response = requests.get(stream_url, stream=True)
        if 'icy-metaint' in response.headers:
            metaint_header = int(response.headers['icy-metaint'])
            if metaint_header > 0:
                response.raw.read(metaint_header)  # Discard audio data
                metadata_length = int(response.raw.read(1)[0]) * 16  # Metadata length
                if metadata_length > 0:
                    metadata = response.raw.read(metadata_length).decode('utf-8')
                    metadata = metadata.strip()  # Remove leading/trailing whitespace
                    if metadata.startswith('StreamTitle='):
                        song_info = metadata.replace('StreamTitle=', '').strip("'").strip()
                        # Update the label in the main GUI thread
                        root.after_idle(lambda: current_song_label.configure(text="Current Song: " + song_info))

        response.close()


root = ttk.Window(themename="darkly")
root.geometry("500x500")
root.title("Radio")

volume_slider = ttk.Scale(root, from_=0, to=100, orient=tk.HORIZONTAL, length=400)
volume_slider.set(100)
volume_slider.pack(side=tk.TOP, padx=5, pady=5)

pause_button = ttk.Button(root, text='Pause', bootstyle=DARK, command=pause_radio)
pause_button.pack(side=BOTTOM, padx=10, pady="10")

play_button = ttk.Button(root, text='Play', bootstyle=DARK, command=play_radio)
play_button.pack(side=BOTTOM, padx=5, pady=10)

label = ttk.Label(root, text="PyWaveTunes", font=("Arial", 30))
label.pack(side=TOP, padx=5, pady=5)

selected_stream = StringVar()
streams = ["http://radio886.at/streams/radio_88.6/mp3", "http://radio886.at/streams/88.6_Classic_Rock/mp3"]
stream_cb = ttk.Combobox(root, values=streams, textvariable=selected_stream, font=("Arial", 15), width=50, state="readonly")
stream_cb.pack(side=TOP, padx=5, pady=50)

volume_label = ttk.Label(root, text="Volume:", font=("Arial", 15))
volume_label.pack(side=TOP, padx=5, pady=5)

volume_slider.bind("<ButtonRelease-1>", change_volume)
volume_slider.bind("<B1-Motion>", change_volume)
stream_cb.bind("<<ComboboxSelected>>", change_volume)
play_button.bind("<ButtonRelease-1>", change_volume)

tabControl = ttk.Notebook(root)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text="Streams")
tabControl.pack(side="top", expand=1, fill="both")

tab2 = ttk.Frame(tabControl)
tabControl.add(tab2, text="Settings")
tabControl.pack(side="top", expand=1, fill="both")

current_stream_label = ttk.Label(tab1, text="Song: " + selected_stream.get(), font=("Arial", 15))
current_stream_label.pack(padx=5, pady=5)
current_song_label = ttk.Label(tab1, text="Current Song:", font=("Arial", 15))
current_song_label.pack(padx=5, pady=5)

fetch_thread = threading.Thread(target=fetch_radio_metadata)
fetch_thread.daemon = True
fetch_thread.start()

root.mainloop()
