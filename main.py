import tkinter
import threading
from acrcloud.recognizer import ACRCloudRecognizer
from scipy.io.wavfile import write
from time import sleep
import sounddevice as sd
import json
import os
from graph import plot

# colors
babyblue = "#CDDEFF"

class AsyncRecognizer(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        while True:

            # API keys, fill with keys from acrcloud.com
            app.button.config(text="Quit program", command=lambda: os._exit(0))

            access_key = os.environ.get('colinde_access_key')
            secret_key = os.environ.get('colinde_secret_key')
            # var init
            wait_time = 1  # seconds to wait between recordings
            last_song = "n/a"
            data = open("output.json", "r")
            db = json.load(data)
            song_playing = "n/a"

            def timer(duration):
                while duration:
                    sleep(1)
                    duration -= 1

            def record_audio(filename):
                # frequency
                fs = 44100  # frames per second to capture
                duration = 8  # recording duration in seconds
                print("Recording..........")
                app.lowerlabel.config(text="Recording...")
                if last_song != "n/a":
                    app.upperlabel.config(text=f"The last song was {last_song}.")
                # start recording
                recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
                timer(duration)  # call timer function
                sd.wait()
                # write the data in filename and save it
                write(filename, fs, recording)

            while True:

                # start recording
                filename = "rec.mp3"
                record_audio(filename)
                app.auxlabel.config(text="")
                # init song recognition API
                config = {
                    'host': 'identify-eu-west-1.acrcloud.com',
                    'access_key': access_key,
                    'access_secret': secret_key,
                    'debug': False,
                    'timeout': 10
                }
                acrcloud = ACRCloudRecognizer(config)
                data = acrcloud.recognize_by_file('rec.mp3', 0)

                try:
                    json_result = json.loads(data)
                    song_playing = json_result["metadata"]["music"][0]["title"]
                    artist = json_result["metadata"]["music"][0]["artists"][0]["name"]
                    file_entry = song_playing + " by " + artist
                    print(f"The song currently playing is {file_entry}.")
                    app.lowerlabel.config(text=f"The song currently playing is {file_entry}.")
                    sleep(3)
                    last_song_recognized = True

                except KeyError:
                    print("No song could be recognized.")
                    app.lowerlabel.config(text="No song could be recognized.")
                    sleep(3)
                    last_song_recognized = False

                if last_song_recognized and last_song.strip() != song_playing.strip():
                    if db.get(file_entry) is not None:
                        print("This song is in the database.")
                        app.auxlabel.config(text="This song has been recognized before.")
                        sleep(3)
                        app.auxlabel.config(text="")
                        db[file_entry] += 1
                    else:
                        db[file_entry] = 1
                        print("This is a new song!")
                        app.auxlabel.config(text="This is a new song!")
                        sleep(3)
                        app.auxlabel.config(text="")
                    file = open("output.json", "w")
                    json.dump(db, file, indent=4)
                    file.close()

                else:
                    if last_song_recognized:
                        print("This instance has already been registered.")
                        app.auxlabel.config(text="This instance has already been registered.")
                        sleep(3)
                        app.auxlabel.config(text="")
                last_song = song_playing
                sleep(wait_time)


class Gui(tkinter.Tk):
    def __init__(self):
        super().__init__()

        # window properties
        self.title("Song Recognizer")
        self.minsize(width=800, height=450)

        # label
        self.upperlabel = tkinter.Label(text="", font=("Century Gothic", 16), bg=babyblue)
        self.auxlabel = tkinter.Label(text="", font=("Century Gothic", 14), bg=babyblue)
        self.lowerlabel = tkinter.Label(text="Start recording when ready.", font=("Century Gothic", 18), bg=babyblue)

        self.upperlabel.pack(expand=True)
        self.auxlabel.pack(expand=True)
        self.lowerlabel.pack(expand=True)

        # button
        self.button = tkinter.Button(text="Start Recording", command=self.call_engine, font=("Century Gothic", 12),
                                     bg=babyblue)
        self.plot_button = tkinter.Button(text="Plot Graph", command=plot, font=("Century Gothic", 10), bg=babyblue)
        self.button.pack(expand=True)
        self.plot_button.pack(expand=True)

    def call_engine(self):
        instance = AsyncRecognizer()
        instance.start()


if __name__ == '__main__':
    app = Gui()
    app.config(bg=babyblue)
    app.mainloop()
