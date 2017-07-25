# Takes a log file and writes out files separated by day

import sys, datetime

inputfile = sys.argv[1]

def write(filename, line):
    writefile = open(filename,'a')
    writefile.write(line)
    writefile.write('\n')
    writefile.close()

with open(inputfile,'r') as f:
	for line in f:
		line = line.strip()
		line = line.replace('  ',' ')	# Some lines have double spaces. This gets rid of that.
		ls = line.split(' ')
		if len(ls) > 7:
			dateandtime = ('{0}:{1}:{2}'.format(ls[0],ls[1],ls[2]))
			try:
				dt = datetime.datetime.strptime(dateandtime, '%b:%d:%H:%M:%S')
				dt = dt.replace(year=2017) # year isn't specified, so I have to put it in
			except:
				continue

			daycount = 1
			while daycount <= 30:
				if ls[1] == str(daycount):
					filename = ('{0}{1}.txt'.format(ls[0],ls[1]))
					write(filename,line)
				daycount +=1
