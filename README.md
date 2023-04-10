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

| Subcommand | Description | Flags 
|--|--|--|    
|download  | Download a youtube <br>video from the given URL |&nbsp;--url: video URL <br> --filetype: video filetype, mp3/mp4  |
|playlist| Download a youtube  playlist from the <br>given URL | &nbsp; --url, --filetype, <br> &nbsp; --max-num: Only download the first <i>n</i> videos from the playlist|
|clean|Remove all files from the downloads<br> directory this script downloads videos to| None
|help|Displays a list of subcommands|None



## Example commands

#### Download a youtube video

```
python ycl.py download --url=https://www.youtube.com/watch?v=dQw4w9WgXcQ --filetype=mp4
```

#### Download a playlist
```
python ycl.py playlist --url=https://www.youtube.com/playlist?list=PLFuNbp0NQ1D9ZMiyspdMS2hLtliqk9hVn --filetype=mp4
```
