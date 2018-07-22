import subprocess
import os
import click
import re
import datetime

from string import Formatter
from datetime import timedelta


def strfdelta_my_Version(time_delta):

	days, seconds = time_delta.days, time_delta.seconds

	hours = days * 24 + seconds // 3600
	minutes = (seconds % 3600) // 60
	seconds = seconds % 60

	return '{0:02d}:{1:02d}:{2:02d}'.format(hours, minutes, seconds)


def strfdelta(tdelta, fmt='{H:02}:{M:02}:{S:02}', inputtype='timedelta'):
	"""Convert a datetime.timedelta object or a regular number to a custom-
	formatted string, just like the stftime() method does for datetime.datetime
	objects.

	The fmt argument allows custom formatting to be specified.  Fields can 
	include seconds, minutes, hours, days, and weeks.  Each field is optional.

	Some examples:
					'{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
					'{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
					'{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
					'{H}h {S}s'                       --> '72h 800s'

	The inputtype argument allows tdelta to be a regular number instead of the  
	default, which is a datetime.timedelta object.  Valid inputtype strings: 
					's', 'seconds', 
					'm', 'minutes', 
					'h', 'hours', 
					'd', 'days', 
					'w', 'weeks'
	"""

	# Convert tdelta to integer seconds.
	if inputtype == 'timedelta':
		remainder = int(tdelta.total_seconds())
	elif inputtype in ['s', 'seconds']:
		remainder = int(tdelta)
	elif inputtype in ['m', 'minutes']:
		remainder = int(tdelta)*60
	elif inputtype in ['h', 'hours']:
		remainder = int(tdelta)*3600
	elif inputtype in ['d', 'days']:
		remainder = int(tdelta)*86400
	elif inputtype in ['w', 'weeks']:
		remainder = int(tdelta)*604800

	f = Formatter()
	desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
	possible_fields = ('W', 'D', 'H', 'M', 'S')
	constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
	values = {}
	for field in possible_fields:
		if field in desired_fields and field in constants:
			values[field], remainder = divmod(remainder, constants[field])
	return f.format(fmt, **values)


def getDuration(file):
	process = subprocess.Popen(
		['ffmpeg',  '-i', file], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
	stdout, stderr = process.communicate()
	matches = re.search(
		r"Duration:\s{1}(?P<hours>\d+?):(?P<minutes>\d+?):(?P<seconds>\d+\.\d+?),", str(stdout), re.DOTALL).groupdict()
	return matches


def get_endtime(inputfile, time):

	matches = getDuration(inputfile)

	sec = matches['seconds']
	sec = sec if '.' not in sec else sec.split('.')[0]
	params = {
		"seconds" 	: int(sec),
		"minutes" 	: int(matches['minutes']),
		"hours" 	: int(matches['hours'])
	}

	file_duration = datetime.timedelta(**params)
	my_time = datetime.timedelta(seconds=int(time))

	wanted_time = file_duration - my_time
	return strfdelta(wanted_time)


# @click.option('-timef', default='59:59:59', help='Amount of trim time. Format:HHMMSS')
@click.command()
@click.option('-i', default='', help='Input movie')
@click.option('-time', default=0, help='Amount of trim time. Format: #seconds')
@click.option('-l', is_flag=True, default=True, help='trim from left. Used by default')
@click.option('-r', is_flag=True, default=False, help='trim from right')
@click.option('-y', is_flag=True, default=False, help='force overwrite')
def cli(i, time, l, r, y):
	'''
	Tool for trimming parts of video/audio file

	Examples:

	1) cut 1.mp4 -time 5	
	>>> left trim 5sec

	2) cut 1.mp4 -time 5 -r	
	>>> right trim 5sec

	3) cut 1.mp4 -time 5 -r -y	
	>>> right trim 5sec + force overwrite
	'''

	# 			 #
	# Validation #
	# 			 #
	if i == '':
		click.echo(f"I don't have a file, can't do it.")
		return

	if len(str(time)) > 6:
		click.echo(f"time is too long.")
		return

	# 			 #
	# Programm	 #
	# 			 #

	file, ext = os.path.splitext(i)
	new_file_name = f'{file}_ffmpeg_result{ext}'

	# y flag
	ffmpeg = 'ffmpeg' if y else 'ffmpeg -y'

	if r:
		end_time = get_endtime(i, time)
		command = f'{ffmpeg} -i "{i}" -to {end_time} -c copy "{new_file_name}"'
	elif l:
		command = f'{ffmpeg} -i "{i}" -ss {time} -c copy "{new_file_name}"'

	click.echo(f' command = {command}')
	click.echo('\n' * 5)

	# subprocess.Popen(command, shell=True)
	os.system(command)


if __name__ == '__main__':
	cli()
