# YCL: The youtube command line downloader
A python command-line tool for everyone fed up with those sketchy youtube downloader sites that open 3 popups whenever you click something.

# Installation
Download `ycl.py` and `requirements.txt ` or use the following command to clone into the repository:
```
git clone "https://github.com/mistertoenails/YCL" ycl
```
Install the project dependencies using this command:
```
pip install -r requirements.txt
```
Then, run the python script using this command:
```
python ycl.py <subcommand> <flags>
```

# Subcommands and flags

```
SUBCOMMANDS:

SUBCOMMAND   USAGE
------------------------------------------------
download:    Download a youtube video from a URL.
playlist:    Download a youtube playlist.
clean:       Empty the directory this script downloads videos to.
help:        Show a list of subcommands
search:      Search for a given query instead of downloading a URL.


DOWNLOAD:

FLAG         USAGE
------------------------------------------------------------
--url:       The URL to download from. 
--filetype:  The filetype to download videos as. mp3 or mp4.
-------------------------------------------------------------


PLAYLIST:

FLAG         USAGE
------------------------------------------------------------
--url:       The playlist URL.
--filetype:  The filetype to download videos as. mp3 or mp4.
--max-num:   The maximum number of videos to download.
------------------------------------------------------------


SEARCH:

FLAG           USAGE
---------------------------------------------------------------------
--query:         Search query to use
--filtype:       The filetype to download videos as. mp3 or mp4.
--first:         Don't ask for a selection, download first result.
--display-num:   The number of search results to display. Default 10.
---------------------------------------------------------------------


HELP:

FLAG         USAGE
------------------------------------------------------------
no flags yet
------------------------------------------------------------


CLEAN:

FLAG         USAGE
------------------------------------------------------------
no flags yet
------------------------------------------------------------


```
## Notes
- If the url and filetype (or query and filetype) flags aren't provided, you will be prompted for them.


