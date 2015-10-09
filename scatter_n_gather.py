#TO DO:
#	1) add dictionary to all_urls for non-repetitive/looping of links
#	2) fix random urls that are producing incorrect download urls
#	3) better log features (create log file with time stamp of thread+task+function information)

from threading import Thread, current_thread
from multiprocessing import Process, Lock
import threading
import time
import sys
import os
import time
import urllib
import urllib2
import re 
import socket

#used to limit the effect of "hanging" on a retrieve request for an image
socket.setdefaulttimeout(1)

def help_msg ():
	print ("\nUSAGE: [-option] [parameter]")
	print ("\n")
	print ("options")
	print ("       -m        Number of images to download.")
	print ("       -w        URL to download images from.")
	print ("       -d        Directory to download images WRT current directory")
	print ("\n")
	print ("EXAMPLE: scrapper.py -d pics -w www.reddit.com -m 100")
	print ("downloads the first 100 images from reddit and places into pics folder")

#call function by passing in url of website
#will set up the HTML structure (in order of tag appearance) and return list
def setup_url_html_structure (url):
	response = urllib2.urlopen(url)
	HTML = response.read()
	
	elements = []		#stores each individual element in webpage
	word = "" 			#temp. variable to store element


	start_of_element = False
	#creates and stores each element in webpage
	for letter in HTML:
		if (letter == "<"):
			start_of_element = True
		if (letter == ">"):
			start_of_element = False
			word+=">"
		if (start_of_element):
			word+=letter
		if (not start_of_element):
			elements.append(word)
			word = ""

	elements = filter(None, elements)		#removes empty entries
	return elements

#requires list of html tags as parameter to sort through
#returns list of only urls with picture
def locate_url_of_pictures(html_structure): 
	pictures = [] 	#stores all pictures
	#--------------------STRENGTHEN THIS SEARCH ALGROTHIM TO BETTER ACCODMIDATE DIFFERENT WEBSITES (YOUTUBE FOR EXAMPLE)--------------------#
	#finding pictures in the list of elements by scanning for img related tags
	for element in html_structure:
		if ("img" in element):
			element = element.split(' ')
			for tag in element:
				if ("src" in tag):
					pictures.append(tag)
	return pictures

def locate_url_of_suburls(html_structure):
	urls = []
	for element in html_structure:
		if ("href" in element):
			element = element.split(' ')
			for tag in element:
				if ("href" in tag):
					tmp_url = tag[6:-1]
					#keep adding to list, hot fix....
					if ((".com" in tmp_url) or (".ca" in tmp_url) or (".org" in tmp_url) or (".gov" in tmp_url)):
						if (tmp_url[0:2] == "//"):
							tmp_url = "http:" + tmp_url
						elif (tmp_url[0] == "/"):
							tmp_url = "http://" + base_url + tmp_url
					else:
						if (tmp_url[0] == '/'):
							tmp_url = "http://" + base_url + tmp_url
						else:
							tmp_url = "http://" + base_url + '/' + tmp_url
					#add the try except statements for adding http: in front or not here.
					urls.append(tmp_url)
					url_semaphore.release()
	return urls

def download_based_on_url(url_list):
	#downloading the pictures and storing them to a respective location 
	global num_of_pic_to_dwnld
	url = ""
	for pic in url_list:
		if (num_of_pic_to_dwnld == 0):
			break;
		filename = time.time()*10
		url = pic[5:-1]
		url = re.sub('["]', '', url)
		http_url = url
		if ("http" not in url):
			http_url = "http:"+url
		try:
			image = urllib.URLopener()
			image.retrieve(http_url,str(filename)+".jpg")
			#print(http_url)
		except:
			try:
				if (url[0] == '/'):
					url = "http://" + base_url + url
				else:
					url = "http://" + base_url + '/' + url
				image = urllib.URLopener()
				image.retrieve(url,str(filename)+".jpg")
				#print(url)
			except:
				print("Error was thrown because of: " + url)
		num_of_pic_to_dwnld -= 1;

def main_process ():
	global global_url_index
	global all_urls
	url_semaphore.acquire()
	with array_index_mutex:
		array_index = global_url_index
		global_url_index += 1
	html_structure = setup_url_html_structure (all_urls[array_index])
	all_urls = all_urls + locate_url_of_suburls (html_structure)
	picture_url = locate_url_of_pictures (html_structure)

	download_based_on_url (picture_url)

num_of_pic_to_dwnld = 1000000
base_url = ""
url_to_dwnld = "http://"
directory_to_dwnld = ""
all_urls = []
global_url_index = 0
url_semaphore = threading.Semaphore(value=1)
array_index_mutex = Lock()

if ((len(sys.argv) <= 2) or (len(sys.argv) >= 8) or ("help" in sys.argv)):
	help_msg()
	exit()
if ("-m" in sys.argv):
	num_of_pic_to_dwnld = int(sys.argv[sys.argv.index("-m") + 1])
if ("-w" in sys.argv):
	tmp = sys.argv[sys.argv.index("-w") + 1]
	url_to_dwnld += tmp
	try:
		base_url = tmp[tmp.index('w'):tmp.index('/')]
	except:
		base_url = tmp[tmp.index('w'):]
if ("-d" in sys.argv):
	directory_to_dwnld = "\\" + sys.argv[sys.argv.index("-d") + 1]
	os.chdir(os.getcwd()+directory_to_dwnld)

all_urls.append(url_to_dwnld)

#MULTI THREADED
i = 0
while (num_of_pic_to_dwnld != 0):
	if (threading.activeCount() < 5):
		i += 1
		thread = Thread(target = main_process, name=str(i))
		thread.start()

#SINGLE THREADED APPROACH
# while (num_of_pic_to_dwnld != 0):

# 	print (all_urls[global_url_index])
# 	print (global_url_index)

# 	html_structure = setup_url_html_structure (all_urls[global_url_index])
# 	picture_url = locate_url_of_pictures (html_structure)
# 	download_based_on_url (picture_url)

# 	tmp_list_of_urls = locate_url_of_suburls (html_structure)
# 	all_urls = all_urls + tmp_list_of_urls
# 	global_url_index += 1
