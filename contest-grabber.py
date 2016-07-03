#!/usr/bin/env python

######################################################
# NOTE:  do not call this file directly.
# use build-ff-book.sh instead.
######################################################


import sys
from sys import version_info
import os.path
import os, shutil
import datetime
import urllib2
import urllib
import unicodedata
import re
import codecs
import requests
import json
import string
import hashlib
from pyquery import PyQuery as pq
import HTMLParser
from dateutil import parser
import ffParseTools



def fetchData(options):

	urls = []
	storyTitles = []
	
	######################################################
	# grab the initial html and all of the urls.

	if not os.path.isfile("cache/urls.json"):
		print "Fetching from URL"

		# fix weird characters in the url
		options['submissionUrl'] = options['submissionUrl'].replace("!", "%21")
		options['votingUrl'] = options['votingUrl'].replace("!", "%21")

		print "Writing out options"
		target = codecs.open("cache/options.json", 'w', "utf-8")
		target.write(json.dumps(options))
		target.close()

		urls.append({"url":options['submissionUrl'], "hash":hashlib.md5(options['submissionUrl']).hexdigest()})

		htmlString = requests.get(options['submissionUrl']).text
		metaData = ffParseTools.getMetadata(htmlString, options)

		htmlObj = pq(htmlString)
		navs = htmlObj.find('.navPages')
		for node in navs:
			tempUrl = node.attrib['href'].replace("!", "%21")
			urls.append({"url":tempUrl, "hash":hashlib.md5(tempUrl).hexdigest()})

		#urls = sorted(set(urls))
		print "Parsed URLs"
		for urlData in urls:
			print urlData['hash'] + ": " + urlData['url']

		# writing out the url json to file
		target = codecs.open("cache/urls.json", 'w', "utf-8")
		target.write(json.dumps(urls))
		target.close()

	else:
		oldOptions = options
		print "Fetching options from CACHE"
		file = open("cache/options.json", 'r')
		options = json.loads(file.read())
		file.close()
		options["showAuthor"] = oldOptions['showAuthor'] 
		options["useCache"] = oldOptions['useCache'] 

		print "Fetching data from CACHE"
		file = open("cache/urls.json", 'r')
		urls = json.loads(file.read())
		file.close()

		file = open("cache/" + urls[0]['hash'], 'r')
		htmlString = file.read().decode("utf8")
		metaData = ffParseTools.getMetadata(htmlString, options)


	#return metaData

	######################################################
	# parse out all the story titles from the voting page.

	if not os.path.isfile("cache/storyTitles.json"):
		print "Fetching storyTitles from URL"

		htmlString = requests.get(options['votingUrl']).text
		htmlObj = pq(htmlString)
		votes = htmlObj.find('#poll_options')

		if len(votes) >= 1:
			print "pulling titles from poll"
			storyLabels = pq(votes).find('dt')

			for labelNode in storyLabels:
				storyTitles.append(pq(labelNode).text())
				print pq(labelNode).text()

		# writing out the url json to file
		target = codecs.open("cache/storyTitles.json", 'w', "utf-8")
		target.write(json.dumps(storyTitles))
		target.close()

	else:
		print "Fetching storyTitles from CACHE"
		file = open("cache/storyTitles.json", 'r')
		storyTitles = json.loads(file.read())
		file.close()



	######################################################
	# pull down all the stories

	storyCount = 0

	for urlData in urls:

		print "working on page: " + urlData['hash'] + ": " + urlData['url']
		pageHtml = ""

		if not os.path.isfile("cache/" + urls[0]['hash']):
			print "Fetching pageHtml from URL"

			request = urllib2.Request(urlData['url'])
			request.add_header('Accept-Encoding', 'utf-8')
			response = urllib2.urlopen(request)
			pageHtml = response.read().decode('utf-8', 'ignore')

			target = codecs.open("cache/" + urls[0]['hash'], 'w', "utf-8")
			target.write(pageHtml)
			target.close()

		else:
			print "Fetching pageHtml from CACHE"
			file = open("cache/" + urls[0]['hash'], 'r')
			pageHtml = file.read().decode("utf8")
			file.close()


		htmlObj = pq(pageHtml)
		posts = htmlObj.find('.post_wrapper')

		for postNode in posts:
			post = pq(postNode)

			# skip the instruction post
			if posts.eq(0) != post:
				story = ffParseTools.processPost(post, storyTitles)

				if story is not None:
					storyCount = storyCount + 1
					story['index'] = str(storyCount)

					print str(storyCount) + ") " + story['author']
					metaData['stories'].append(story)


	#print metaData['stories'][9]['html']
	return metaData


def writeConf(metaData):
	# writing out the conf file for the shell script ebook publishing
	target = codecs.open("ebook.conf", 'w', "utf-8")
	target.truncate()
	target.write('Title="' + metaData['Title'] + '"\n')
	target.write('ShortTitle="' + metaData['ShortTitle'] + '"\n')
	target.write('Subtitle="' + metaData['Subtitle'] + '"\n')
	target.write('Series="' + metaData['Series'] + '"\n')
	target.write('ContestMonth="' + metaData['ContestMonth'] + '"\n')
	target.write('ShowAuthor=' + str(metaData['ShowAuthor']) + '\n')
	target.write('Author="' + metaData['Author'] + '"\n')
	target.write('ImageUrl="' + metaData['ImageUrl'] + '"\n')
	target.close()

	# writing out the json config for the book text reader
	jsonMetadata = {}
	jsonMetadata['title'] = metaData['Title']
	jsonMetadata['author'] = metaData['Author']
	jsonMetadata['thumbnail'] = "http://m3mnoch.com/static/ff-books/covers/" + metaData['ShortTitle'] + "-cover.jpg"
	jsonMetadata['description'] = metaData['introText']
	target = codecs.open("metadata.json", 'w', "utf-8")
	target.write(json.dumps(jsonMetadata))
	target.close()


def writeHtml(metaData):

	print "compiling html...\n"

	htmlOut = ""
	htmlOut = htmlOut + '<!DOCTYPE html><html><head><meta charset="utf-8"/>'
	htmlOut = htmlOut + '<title>' + metaData['Title'] + '</title>'
	htmlOut = htmlOut + '<meta name="subtitle" content="' + metaData['Subtitle'] + '"/>'
	htmlOut = htmlOut + '<meta name="author" content="' + metaData['Author'] + '"/>'
	htmlOut = htmlOut + '<meta name="date" content="' + metaData['Date'] + '"/>'
	htmlOut = htmlOut + '<meta name="revision" content="' + metaData['Revision'] + '"/>'
	htmlOut = htmlOut + '<meta name="shorttitle" content="' + metaData['ShortTitle'] + '"/>'
	htmlOut = htmlOut + '<meta name="series" content="' + metaData['Series'] + '"/>'
	htmlOut = htmlOut + '<meta name="cover" content="cover.jpg"/>'
	htmlOut = htmlOut + '<link href="https://fonts.googleapis.com/css?family=Libre+Baskerville:400,400italic,700" rel="stylesheet" type="text/css">'
	htmlOut = htmlOut + '<link type="text/css" rel="stylesheet" href="' + metaData['CSS'] + '"/>'
	htmlOut = htmlOut + '<meta name="format" content="complete"/>'
	htmlOut = htmlOut + '</head><body>'

	htmlOut = htmlOut + '<h1 class="booktitle">' + metaData['Title'] + '</h1>'
	htmlOut = htmlOut + '<h3>' + metaData['Subtitle'] + '</h3>'
	htmlOut = htmlOut + '<p>' + metaData['introText'] + '</p>'

	htmlOut = htmlOut + '<h1>Table of Contents</h1>'
	htmlOut = htmlOut + '<ol class="toc">'
	for story in metaData['stories']:
		htmlOut = htmlOut + '<li><a href="#story' + story['index'] + '">' + story['title'] + ' by ' + story['author'] + '</a></li>'
	htmlOut = htmlOut + '</ol>'

	# global image counter
	imageCount = 0

	for story in metaData['stories']:

		if not os.path.isfile("cache/" + story['author'] + ".html"):
			print "Generating story html"
			storyHtmlString = ffParseTools.formatStoryHtml(story, metaData)

			target = codecs.open("cache/" + story['author'] + ".html", 'w', "utf-8")
			target.truncate()
			target.write(storyHtmlString)
			target.close()

		else:
			print "Fetching cleaned pageHtml from CACHE"
			file = open("cache/" + story['author'] + ".html", 'r')
			storyHtmlString = file.read().decode("utf8")
			file.close()

		# we are just going to keep rewriting the original html.
		target = codecs.open("cache/" + story['author'] + "-original.html", 'w', "utf-8")
		target.truncate()
		target.write(story['html'])
		target.close()

		htmlOut = htmlOut + storyHtmlString

	htmlOut = htmlOut + '</body></html>'

	target = codecs.open("output/" + metaData['ShortTitle'] + ".html", 'w', "utf-8")
	target.truncate()
	target.write(htmlOut)
	target.close()

	target = codecs.open("output/" + metaData['ShortTitle'] + "-rtf.html", 'w+', "utf-8")
	target.truncate()
	target.write(htmlOut.replace("src=\"images", "src=\"" + os.getcwd() + "/output/images"))
	target.close()
	
	return True

def writeCritTemplate(metaData):

	print "building critique templates...\n"

	# clean out the old one.
	target = codecs.open("critiques-" + metaData['ShortTitle'] + ".md", 'w+', "utf-8")
	target.truncate()

	target.write('# Fantasy Faction Critique Template\n')
	target.write('## ' + metaData['ContestMonth'] + ': ' + metaData['Title'] + '\n')
	target.write('\n\n')

	for story in metaData['stories']:
		target.write('----------------------------------------------------------------\n')
		target.write('## ' + story['title'] + '\n')
		target.write('### By ' + story['author'] + '\n')
		target.write('SCORE: \n')
		target.write('\n')
		target.write('Summary:\n')
		target.write('> \n')
		target.write('\n')
		target.write('Theme Appropriateness:\n')
		target.write('> \n')
		target.write('\n')
		target.write('Opening Strength:\n')
		target.write('> \n')
		target.write('\n')
		target.write('Mechanics and Style:\n')
		target.write('> \n')
		target.write('\n')
		target.write('Characterization:\n')
		target.write('> \n')
		target.write('\n')
		target.write('Conflict and Tension:\n')
		target.write('> \n')
		target.write('\n')
		target.write('Cohesive Story:\n')
		target.write('> \n')
		target.write('\n')
		target.write('Ending Payoff:\n')
		target.write('> \n')
		target.write('\n\n\n')

	target.close()
	return True



def getUserData(questionString):
	py3 = version_info[0] > 2 #creates boolean value for test that Python major version > 2
	if py3:
		response = input(questionString + ": ")
	else:
		response = raw_input(questionString + ": ")

	return response

def deleteCache():
	folder = 'cache'
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			#elif os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as e:
			print(e)


def main(argv):
	#
	# Main

	options = {}

	options["showAuthor"] = getUserData("Show the authors? (y/n)")
	if options["showAuthor"][0].lower() == "y":
		options["showAuthor"] = 1
	else:
		options["showAuthor"] = 0

	options["useCache"] = getUserData("Use existing cache? (y/n)")
	if options["useCache"][0].lower() == "n":
		deleteCache()

		options["submissionUrl"] = getUserData("What is the submissions URL?")
		options["votingUrl"] = getUserData("What is the voting URL?")
		
		print "\nBuilding with authors: " + str(options["showAuthor"]) + "\n"
		print "**********\n**********\nSTART FETCH\n**********\n"

	metaData = fetchData(options)
	writeConf(metaData)
	writeHtml(metaData)
	writeCritTemplate(metaData)

	print "\n**********\nEND FETCH"


if __name__ == "__main__":
	main(sys.argv[1:])
