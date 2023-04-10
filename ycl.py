import os
from pytube import YouTube
from pytube import Playlist
from moviepy.editor import *
import urllib.request

import eyed3
import time
import colorama
import sys
import shutil

from eyed3.id3.frames import ImageFrame
import string
def str_bool(str):
  if str.lower() == "false":
    return False
  elif str.lower() == "true":
    return True
  else: 
    return "err"

def parseFlags(list, args):
  returnlist = {}
  for item in list:
    foundmatch = False
    #Loop through flags given, and find the argument to match them to
    for arg in args:
      if item.startswith(arg + '='):
        returnlist[arg] = item[len(arg) + 1:]
        #Append the object to be returned with a key-value pair of the argument name and the provided value
        foundmatch = True
    if not foundmatch:
      #If no match is found, an invalid argument was given
      print(
        f"Invalid flag '{item}'. Run ycl.py help for a list of subcommands and flags."
      )
      sys.exit()

  return returnlist


try:
  #Quit if no subcommand was given
  subcommand = sys.argv[1]
except:
  print(
    "No subcommand specified. Run 'python ycl.py help' to get a list of available subcommands."
  )
  sys.exit()
#List of subcommands to display WHEN THE HELP SUBCOMMAND IS RUN. This is not the subcommand list that is actually operated on.
subcommands = [{
  "Subcommand": "download",
  "Description": "Download a youtube video from a URL",
  "Arguments": "--url, --filetype"
}, {
  "Subcommand": "clean",
  "Description": "Empties the downloads folder for this tool",
  "Arguments": "None"
}, {
  "Subcommand": "help",
  "Description": "Shows this message",
  "Arguments": "None"
}, {
  "Subcommand": "playlist",
  "Description": "Download a youtube playlist",
  "Arguments": "--url, --filetype, --max-num"
}]
DOWNLOAD_DIR = 'downloads'


def print_table(data):
  # Get keys of the data
  headers = list(data[0].keys())


  # Use longest header/value length to calculate width
  col_widths = {}
  for header in headers:
    col_widths[header] = max(len(str(header)),
                             max(len(str(item[header])) for item in data))

  # Print top line
  print(
    f'+{"+".join(["-" * (col_widths[header] + 2) for header in headers])}+')

  # Print column headers
  for header in headers:
    print(f'| {header:{col_widths[header]}} ', end='')
  print('|')

  # Print divider
  for header in headers:
    print(f'+{"-" * (col_widths[header] + 2)}', end='')
  print('+')

  # Print data
  for item in data:
    for header in headers:
      print(f'| {str(item[header]):{col_widths[header]}} ', end='')
    print('|')

    # Print row separator
    for header in headers:
      print(f'+{"-" * (col_widths[header] + 2)}', end='')
    print('+')


def sanitize(s):
  # Some black magic string fuckery, IDK ask chatgpt
  valid_chars = set("-_.() %s%s" % (string.ascii_letters, string.digits))
  s = ''.join(c for c in s if c in valid_chars)
  return s


def add_image_to_mp3(title, verbose=True):
  #Load in the audio file
  audiofile = eyed3.load(title + ".mp3")
  if verbose == True:
    print(
      f"Loaded audio file at {colorama.Fore.BLUE}{os.path.abspath(title + '.mp3')}{colorama.Fore.RED}"
    )
  #Create a tag for the audio file
  if (audiofile.tag == None):
    if verbose == True: print("Initializing tag...")
    audiofile.initTag()

  #Add the image tag
  audiofile.tag.images.set(ImageFrame.FRONT_COVER,
                           open(title + ".jpg", 'rb').read(), 'image/jpeg')
  if verbose == True:
    print(
      f"Added image '{colorama.Fore.BLUE}{os.path.abspath(title+'.jpg')}{colorama.Fore.RED}' to audio file '{colorama.Fore.BLUE}{os.path.abspath(title+'.mp3')}{colorama.Fore.RED}'"
    )
  #Save the tag and delete the image file now that we've added it
  audiofile.tag.save()
  if verbose == True: print("Saved image tag")
  if verbose == True: print("Cleaning up junk files...")
  os.remove(title + '.jpg')
  if verbose == True: print("Finished adding image.")


def download_youtube_video(url):
  yt = YouTube(url)

  #Get the youtube video as a stream and download it
  stream = yt.streams.filter(
    file_extension='mp4').first() 
  output_path = os.path.join(os.getcwd(), 'downloads')

  #Make the downloads directory if it doesn't exist
  if not os.path.exists(output_path):
    os.makedirs(output_path)
  stream.download(output_path=output_path)

 
def download_youtube_audio(url,
                           verbose=True,
                           audio_codec='mp3',
                           audio_bitrate=320):
  #setup
  if verbose == True:
    print(
      f"Invoking download for filetype '{colorama.Fore.BLUE}MP3{colorama.Fore.RED}'"
    )
  yt = YouTube(url)
  if verbose == True:
    print(
      f"Invoked youtube object for video '{colorama.Fore.BLUE}{yt.title}{colorama.Fore.RED}'"
    )
  yt.title = sanitize(yt.title)
  if verbose == True: print("Sanitized title")
  if verbose == True: print("finding download directory...")
  # Create the download directory if it doesn't exist
  if not os.path.exists(DOWNLOAD_DIR):
    if verbose == True: print("Download directory not found")
    os.makedirs(DOWNLOAD_DIR)
    if verbose == True:
      print(
        f"Created downloads directory, stored at absolute path '{colorama.Fore.BLUE}{os.path.abspath(DOWNLOAD_DIR)}{colorama.Fore.RED}'"
      )
  # Download the thumbnail image
  if verbose == True:
    print(
      f"Retreiving video thumbnail from URL '{colorama.Fore.BLUE}{yt.thumbnail_url}{colorama.Fore.RED}'"
    )
  urllib.request.urlretrieve(yt.thumbnail_url,
                             os.path.join(DOWNLOAD_DIR, yt.title + '.jpg'))
  if verbose == True:
    print(
      f"Downloaded thumbnail to absolute path '{colorama.Fore.BLUE}{os.path.abspath(DOWNLOAD_DIR+ '/'+ yt.title + '.jpg')}{colorama.Fore.RED}'"
    )

  # Download the audio file
  if verbose == True: print("Invoking audio stream...")
  audio_stream = yt.streams.filter(only_audio=True).first()
  if verbose == True: print("Downloading audio stream...")
  audio_file = audio_stream.download(output_path=DOWNLOAD_DIR)
  audio_file_name = os.path.splitext(audio_file)[0] + f'.{audio_codec}'
  if verbose == True:
    print(
      f"Downloaded audio file to absolute path '{colorama.Fore.BLUE}{os.path.abspath(audio_file_name)}{colorama.Fore.RED}'"
    )

  # Convert and tag the audio file
  if verbose == True: print("Generating audio clip...")
  audio_clip = AudioFileClip(audio_file)

  audio_clip.write_audiofile(os.path.join(DOWNLOAD_DIR, audio_file_name),
                             codec=audio_codec,
                             bitrate=f"{audio_bitrate}k")
  audio_clip.close()
  if verbose == True: print("Generated audio clip")
  # Replace MP3 file with one with a thumbnail image
  os.remove(audio_file)
  if verbose == True: print("Adding image to MP3 file...")
  add_image_to_mp3(os.path.join(DOWNLOAD_DIR, yt.title), verbose)
  if verbose == True:
    print(
      f"Finished downloading youtube video '{colorama.Fore.BLUE}{yt.title}{colorama.Fore.RED}'"
    )
  return audio_file_name




# Logo stored as a multiline string, with some spacing fuckery
BOX_WIDTH = 55
BOX_HEIGHT = 12
logo = """ 
____________________________________
    ⟋⟋  _      _     _______      _          ⟍⟍      
 //   \\\    //    / -------     ||           \\\  
  ||     \\\  //    / /            ||            ||  
  ||      \\\//    | |             ||            ||  
  ||       ||     | |             ||            ||  
  ||       ||      \ \_______     ||____        ||  
   \\\      ||       \--------|    |_____|      //   
    ⟍⟍________________________________________⟋⟋     
                                                    
      +---------------------------------------+      
      |  The youtube command line downloader  |      
      +---------------------------------------+    

      One file, open source, no ads, no bullshit
      
                                                    
"""
#Print the logo from the multi-line string
def print_logo(): 
  print(f'{colorama.Fore.BLUE}_' + '_' * (BOX_WIDTH + 3) + '_')
  print(f'{colorama.Fore.BLUE}+' + '-' * (BOX_WIDTH + 3) + '+')
  for line in logo.split('\n'):
    time.sleep(0.05)
    if 'The youtube command line downloader' in line:
      padding = ' ' * ((BOX_WIDTH - len(line)) // 2)
      line = padding + line + padding
    else:
      padding = ' ' * ((BOX_WIDTH - len(line)) // 2)
      line = padding + line + padding
    print(
    f'||{colorama.Fore.RED}{" "}{line}{colorama.Fore.BLUE}{" "*(BOX_WIDTH-len(line))}||'
  )
  print(f'{colorama.Fore.BLUE}||' + '_' * (BOX_WIDTH + 1) + '||')
  print('+' + '-' * (BOX_WIDTH + 3) + '+')
  print("\n\n")

#Subcommand funtions
def download_subcommand(args):
  url = ''
  filetype = ''
  #Get argument for the video URL

  try:
    url = args["--url"]
  except:
    url = input(
      f"\n{colorama.Fore.BLUE}Enter a video URL:  \n{colorama.Fore.RED} /> ")

  #Do the same for the filetype
  try:
    filetype = args["--filetype"]
  except:
    filetype = input(
      f"\n{colorama.Fore.BLUE}MP3 or MP4?  \n{colorama.Fore.RED} /> ")
  if filetype.lower() != "mp3" and filetype.lower() != "mp4":
    print("Please enter either MP3 or MP4 as the filetype. Exiting...")
    sys.exit()

  #Check if the provided URL is valid
  try:
    YouTube(url)
  except:
    print(f"{colorama.Fore.BLUE}Invalid youtube URL. Exiting...")
    sys.exit()

  #Check the filetype, then invoke the appropriate function to download the video
  if filetype == "mp4":
    print("Invoking download for type MP4")
    download_youtube_video(url)
  else:
    print("Invoking download for type MP3")
    print(
      f"Finished downloading youtube video to absolute path '{colorama.Fore.BLUE}{os.path.abspath(download_youtube_audio(url))}{colorama.Fore.RED}'"
    )

def help_subcommand(args):
  #I'm usually not a 'code is its own documentation' kinda guy, but seriously
  print_table(subcommands)
  

def clean_subcommand(args):
  #Remove all files from the "downloads" directory the script creates
  print(f"{colorama.Fore.BLUE}Cleaning up downloads...")
  shutil.rmtree("downloads")
  os.mkdir("downloads")
  print(f"{colorama.Fore.BLUE}All done!")

def playlist_subcommand(args):
  url = ''
  filetype = ''
  maxNum = {
    "isMax": False,
    "maxNum": 0
  }
  try:
    maxNum["maxNum"] = int(args['--max-num'])
    maxNum["isMax"] = True
  except:
    pass
  #Get argument for the video URL

  try:
    url = args["--url"]
  except:
    url = input(
      f"\n{colorama.Fore.BLUE}Enter a playlist URL\n{colorama.Fore.RED} /> ")

  #Do the same for the filetype

  try:
    filetype = args["--filetype"]
  except:
    filetype = input(
      f"\n{colorama.Fore.BLUE}MP3 or MP4?  \n{colorama.Fore.RED} /> ")
  try:  
    playlist = Playlist(url)
  except:
    print("Invalid playlist URL. Exiting...")
    sys.exit()

  video_urls = playlist.video_urls

  print(
    f"{colorama.Fore.BLUE}Parsed {len(video_urls)} URLS from playlist '{playlist.title}':\n"
  )
  for url in video_urls:
    
      
    print("[*]  " + url)
  print(
    f"{colorama.Fore.RED}Downloading videos from playlist '{colorama.Fore.BLUE}{playlist.title}{colorama.Fore.RED}'\n"
  )
  index = 0
  for video in video_urls:
    
    if maxNum["isMax"] and index == maxNum["maxNum"]:
      print(f"Downloaded {maxNum['maxNum']} videos. Finishing...")
      break
    index+=1
    yt = YouTube(video)
    print(yt)
    print(
      f"Downloading video '{colorama.Fore.BLUE}{yt.title}{colorama.Fore.RED}'")
    download_youtube_video(video)
    print(
      f"Finished downloading video '{colorama.Fore.BLUE}{yt.title}{colorama.Fore.RED}'\n"
    )
#These are the subcommands that are actually used, the ones up top are just for displaying the 'help' command
_subcommands = [{
  "name": "download",
  "args": ["--url", "--filetype"],
  "function": download_subcommand
}, {
  "name": "help",
  "args": [],
  "function": help_subcommand
}, {
  "name": "clean",
  "args": [],
  "function": clean_subcommand
}, {
  "name": "playlist",
  "args": ["--url", "--filetype", "--max-num"],
  "function": playlist_subcommand
}]

#Parse the subcommand and flags from sys.argv
def parseSubcommand(argList):
  foundMatch = False
  for subcommand in _subcommands:
    flagList = argList[2:]
    if argList[1] == subcommand["name"]:
      foundMatch = True
      if len(subcommand["args"]) == 0 and len(flagList) > 0:
        print("This command doesn't take any arguments. Exiting")
        sys.exit()
      print_logo()
      subcommand["function"](parseFlags(flagList, subcommand["args"]))
      break
  if not foundMatch:
    print("Invalid subcommand. Run 'python ycl.py help' for a list of valid subcommands, or visit PLACEHOLDER_GITHUB_URL for more documentation.")


parseSubcommand(sys.argv)
