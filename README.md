# Tool for trimming parts of video/audio file

### Install:
* ffmpeg
* 'click' module in python

### Examples:

	1) py cut.py 1.mp4 -time 5	
	>>> left trim 5sec

	2) py cut.py 1.mp4 -time 5 -r	
	>>> right trim 5sec

	3) py cut.py 1.mp4 -time 5 -r -y	
	>>> right trim 5sec + force overwrite
