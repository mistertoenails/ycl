import os
from pytube import YouTube
from pytube import Playlist
from pytube import Search
from moviepy.editor import *
import urllib.request
import eyed3
import time
import colorama
import sys
import shutil
from eyed3.id3.frames import ImageFrame
import string


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
      elif item == arg:
        foundmatch = True
        returnlist[arg] = True
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
  stream = yt.streams.filter(file_extension='mp4').first()
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
  print(f"""
  
{colorama.Fore.BLUE}SUBCOMMANDS:{colorama.Fore.RED}

SUBCOMMAND   USAGE
{colorama.Fore.BLUE}-------------------------------------------------{colorama.Fore.RED}
{colorama.Fore.BLUE}download:{colorama.Fore.RED}    Download a youtube video from a URL.
{colorama.Fore.BLUE}playlist:{colorama.Fore.RED}    Download a youtube playlist.
{colorama.Fore.BLUE}clean:{colorama.Fore.RED}       Empty the directory this script downloads videos to.
{colorama.Fore.BLUE}help:{colorama.Fore.RED}        Show a list of subcommands
{colorama.Fore.BLUE}search:{colorama.Fore.RED}      Search for a given query instead of downloading a URL.
{colorama.Fore.BLUE}-------------------------------------------------{colorama.Fore.RED}




{colorama.Fore.BLUE}DOWNLOAD:{colorama.Fore.RED}

FLAG         USAGE
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}
{colorama.Fore.BLUE}--url:{colorama.Fore.RED}       The URL to download from. 
{colorama.Fore.BLUE}--filetype:{colorama.Fore.RED}  The filetype to download videos as. mp3 or mp4.
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}




{colorama.Fore.BLUE}PLAYLIST:{colorama.Fore.RED}

FLAG         USAGE
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}
{colorama.Fore.BLUE}--url:{colorama.Fore.RED}       The playlist URL.
{colorama.Fore.BLUE}--filetype:{colorama.Fore.RED}  The filetype to download videos as. mp3 or mp4.
{colorama.Fore.BLUE}--max-num:{colorama.Fore.RED}   The maximum number of videos to download.
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}




{colorama.Fore.BLUE}SEARCH:{colorama.Fore.RED}

FLAG           USAGE
{colorama.Fore.BLUE}---------------------------------------------------------------------{colorama.Fore.RED}
{colorama.Fore.BLUE}--query:{colorama.Fore.RED}         Search query to use
{colorama.Fore.BLUE}--filtype:{colorama.Fore.RED}       The filetype to download videos as. mp3 or mp4.
{colorama.Fore.BLUE}--first:{colorama.Fore.RED}         Don't ask for a selection, download first result.
{colorama.Fore.BLUE}--display-num:{colorama.Fore.RED}   The number of search results to display. Default 10.
{colorama.Fore.BLUE}---------------------------------------------------------------------{colorama.Fore.RED}




{colorama.Fore.BLUE}HELP:{colorama.Fore.RED}

FLAG         USAGE
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}
{colorama.Fore.BLUE}no flags yet{colorama.Fore.RED}
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}




{colorama.Fore.BLUE}CLEAN:{colorama.Fore.RED}

FLAG         USAGE
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}
{colorama.Fore.BLUE}no flags yet{colorama.Fore.RED}
{colorama.Fore.BLUE}------------------------------------------------------------{colorama.Fore.RED}


  """)


def clean_subcommand(args):
  #Remove all files from the "downloads" directory the script creates
  print(f"{colorama.Fore.BLUE}Cleaning up downloads...")
  shutil.rmtree("downloads")
  os.mkdir("downloads")
  print(f"{colorama.Fore.BLUE}All done!")


def playlist_subcommand(args):
  url = ''
  filetype = ''
  maxNum = {"isMax": False, "maxNum": 0}
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

#Get a list of video URLs from the playlist
  video_urls = playlist.video_urls

  #Some colorama bullshittery
  print(
    f"{colorama.Fore.BLUE}Parsed {len(video_urls)} URLS from playlist '{playlist.title}':\n"
  )
  for url in video_urls:

    print("[*]  " + url)
  print(
    f"{colorama.Fore.RED}Downloading videos from playlist '{colorama.Fore.BLUE}{playlist.title}{colorama.Fore.RED}'\n"
  )

  index = 0
  #Loop through videos
  for video in video_urls:
    #Check if there's a max number of videos to be downloaded
    if maxNum["isMax"] and index == maxNum["maxNum"]:
      print(f"Downloaded {maxNum['maxNum']} videos. Finishing...")
      break
    index += 1
    #Download the video, and some more colorama bullshittery
    yt = YouTube(video)
    print(yt)
    print(
      f"Downloading video '{colorama.Fore.BLUE}{yt.title}{colorama.Fore.RED}'")
    download_youtube_video(video)
    print(
      f"Finished downloading video '{colorama.Fore.BLUE}{yt.title}{colorama.Fore.RED}'\n"
    )


def search_subcommand(args):
  #Get argument values
  try:
    display_num = args["--display-dum"]
    try:
      display_num = int(display_num)
    except:
      print("--display-num requires a valid integer. Exiting...")
      sys.exit()
    if display_num < 1 or display_num > 100:
      print("--display-num must be between 1 and 100. Exiting...")
      sys.exit()
  except:
    display_num = 10
  try:
    use_first = args["--first"]
  except:
    use_first = False
  try:
    query = args["--query"]
  except:
    query = input(
      f"\n{colorama.Fore.BLUE}Enter search query  \n{colorama.Fore.RED} /> ")

  #Search for query provided
  results = Search(query)

  #If the --use-first flag isn't used, loop through the videos with and prompt for a selection
  if not use_first:
    for result in results.results:
      if results.results.index(result) == display_num:
        break
      print(f"""
    {results.results.index(result) + 1}) Title:{colorama.Fore.RED} {result.title}{colorama.Fore.BLUE}
       Channel: {colorama.Fore.RED}{result.author}{colorama.Fore.BLUE}
       Date: {colorama.Fore.RED}{result.publish_date}{colorama.Fore.BLUE}
    """)
    video_index = input(
      f"Which video would you like to download? (enter the video number)\n{colorama.Fore.RED} /> "
    )
    try:
      video_index = int(video_index)
      selected_video = results.results[video_index - 1]
    except:
      print(
        "Please enter a valid number that corresponds to a search result. Quitting..."
      )
      sys.exit()

    print(
      f"Selected video: {colorama.Fore.BLUE}{selected_video.title}{colorama.Fore.RED}"
    )
  else:
    #If the --use-first flag was used, don't display videos, but download the first search result.
    selected_video = results.results[0]
  try:
    filetype = args["--filetype"]
  #Get the filetype if it wasn't specified with a flag
  except:
    filetype = input(
      f"\n{colorama.Fore.BLUE}MP3 or MP4?  \n{colorama.Fore.RED} /> ")
  if filetype.lower() != "mp3" and filetype.lower() != "mp4":
    print("Please enter either MP3 or MP4 as the filetype. Exiting...")
    sys.exit()
  if filetype.lower() == "mp3":
    download_youtube_audio(selected_video.watch_url)
  else:
    download_youtube_video(selected_video.watch_url)


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
}, {
  "name": "search",
  "args": ["--query", "--first", "--display-num", "--filetype"],
  "function": search_subcommand
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
    print(
      "Invalid subcommand. Run 'python ycl.py help' for a list of valid subcommands, or visit https://github.com/mistertoenails/ycl for more documentation."
    )


parseSubcommand(sys.argv)
