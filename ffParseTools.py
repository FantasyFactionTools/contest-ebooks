import os
import sys
import datetime
import urllib2
import urllib
import unicodedata
import re
import codecs

import markdown
import requests
import json
import string
from pyquery import PyQuery as pq
from dateutil import parser

import HTMLParser
from tidylib import tidy_fragment
from lxml.html.clean import clean_html


# define some functions
def getMetadata(htmlString, options):
	######################################################
	# configure the metadata
	metaData = {}
	metaData['stories'] = []
	
	metaData['Title'] = "Current Contest Name"
	metaData['ShortTitle'] = "CurrentContestName"
	metaData['Author'] = "Various Authors"
	metaData['ShowAuthor'] = options['showAuthor']
	metaData['Revision'] = "1.0"
	metaData['Series'] = "Fantasy Faction Writing Contest"
	metaData['CSS'] = "css/ebook.css"

	######################################################
	# find the contest metadata updates
	# WARNING - very, very fragile.

	htmlObj = pq(htmlString)

	if htmlObj.find('.post').eq(0).find('span').eq(0) is not None:
		print "span title"
		metaData['Title'] = htmlObj.find('.post').eq(0).find('span').eq(0).text().strip()

	print "== " + metaData['Title'] + " =="

	metaData['ShortTitle'] = slugify(metaData['Title'])
	if options['showAuthor'] == 0:
		metaData['ShortTitle'] = metaData['ShortTitle'] + "-noauthor"

	metaData['ImageUrl'] = htmlObj.find('.post').eq(0).find('img').eq(0).attr('src')

	rawDateTime = htmlObj.find('.keyinfo .smalltext').eq(0).text()
	print "rawDateTime: " + rawDateTime[6:-2]
	metaData['Date'] = rawDateTime[6:-2]
	contestDate = parser.parse(metaData['Date'])
	metaData['ContestMonth'] = contestDate.strftime("%Y-%M")
	metaData['Subtitle'] = "Fantasy Faction Monthly Writing Contest Anthology, " + contestDate.strftime("%B %Y")

	introText = htmlObj.find('.post').eq(0).html()
	introText = introText.replace("<br />", "--br--")
	introText = pq(introText).text()
	introText = introText.replace(metaData['Title'], "")
	introText = introText[0:introText.find("Rules")]
	metaData['introText'] = introText.replace("--br--","<br />")

	metaData['introText'] = metaData['introText'] + "<p><i>All content originally appeared on the Fantasy Faction Forums in the Monthly Writing Contest.  You can see more information (and even participate in the forums!) on this particular contest by visiting the site.</i><br /><a href='" + options['submissionUrl'] + "'>" + options['submissionUrl'] + "</a></p>"

	return metaData


def processPost(post, storyTitles):
	if post.find('.alt2 div').eq(0).html() is None:
		return None

	else:
		story = {}

		story['author'] = post.find('.poster a').eq(0).text().strip()
		story['title'] = story['author']

		for storyTitle in storyTitles:
			if story['author'] in storyTitle:

				if " - " in storyTitle:
					storyAuthorArray = storyTitle.split(" - ")
				elif ", by " in storyTitle:
					storyAuthorArray = storyTitle.split(", by ")
				elif " by " in storyTitle:
					storyAuthorArray = storyTitle.split(" by ")

				story['title'] = storyAuthorArray[0].strip()
				story['author'] = storyAuthorArray[1].strip()
				break

		print "=== Start Processing: " + story['title'] + " by " + story['author']

		mainBodyObj = post.find('.alt2 div').eq(0)
		spoilerCount = len(mainBodyObj.html())

		print "number of spoiler tags: " + str(len(post.find('.alt2 div')))

		# look for the largest spoiler tag because sometimes there are two.
		# *sigh*
		if len(post.find('.alt2 div')) > 1:
			for possibleBody in post.find('.alt2 div'):
				if pq(possibleBody).html() is not None:
					print "spoilerCount:" + str(spoilerCount) + ", the length:" + str(len(pq(possibleBody).html()))
					if spoilerCount < len(pq(possibleBody).html()):
						spoilerCount = len(pq(possibleBody).html())
						print "new spoilerCount: " + str(spoilerCount)
						mainBodyObj = pq(possibleBody)

		if mainBodyObj.find('.alt2 div') is not None:
			# there's another stupid spoiler in the spoiler.
			# this is pretty janky.
			for spoilerNode in mainBodyObj.find('.alt2 div'):
				spoiler = pq(spoilerNode).clone()
				spoiler.attr("style", "")
				mainBodyObj.append(spoiler)

			for spoilerNode in mainBodyObj.find('.alt2').parents('div'):
				spoiler = pq(spoilerNode).remove()

		story['html'] = mainBodyObj.html()
		story['html'] = ' '.join(story['html'].split()) #story['html'].replace("&nbsp;", "")
		story['html'] = encode_for_xml(story['html'], 'ascii')

	return story


def formatStoryHtml(story, metaData):

	htmlOut = '<div class="shortstory"><h1 id="story' + story['index'] + '">' + story['title'] + '</h1>'

	if metaData['ShowAuthor'] == 1:
		htmlOut = htmlOut + '<h2>By ' + story['author'] + '</h2>'

	story['html'] = "<p>" + story['html'].replace("<br /><br />", "</p><p>") + "</p>"
	story['html'] = story['html'].replace("<br><br>", "</p><p>")
	story['html'] = story['html'].replace("<br />", "</p><p>")
	story['html'] = story['html'].replace("<br>", "</p><p>")
	story['html'] = story['html'].replace("<p> ", "<p>")
	#story['html'] = ' '.join(story['html'].split()) #story['html'].replace("&nbsp;", "")
	story['html'] = story['html'].replace("<p></p>","<p>&nbsp;</p>")

	# lop out the existing title.
	storyObj = pq(story['html'])
	for htmlNode in storyObj.children('p'):
		htmlObj = pq(htmlNode)

		exclude = set(string.punctuation)
		potentialTitle = ''.join(ch for ch in htmlObj.text() if ch not in exclude).lower()
		existingTitle = ''.join(ch for ch in story['title'] if ch not in exclude).lower()
		#print "comparing: " + potentialTitle + "|" + existingTitle

		if potentialTitle == existingTitle:
			print "found p title, removing: " + story['title']
			htmlObj.addClass('nukeMe')
			break

	for htmlNode in storyObj.children('div'):
		htmlObj = pq(htmlNode)

		exclude = set(string.punctuation)
		potentialTitle = ''.join(ch for ch in htmlObj.text() if ch not in exclude).lower()
		existingTitle = ''.join(ch for ch in story['title'] if ch not in exclude).lower()
		#print "comparing: " + potentialTitle + "|" + existingTitle

		if potentialTitle == existingTitle:
			print "found div title, removing: " + story['title']
			htmlObj.addClass('nukeMe')
			break

	#storyObj.remove('.nukeMe')

	# nuke blank nodes before the actual story.
	for htmlNode in storyObj.children('*'):
		htmlObj = pq(htmlNode)
		print "checking for blank node: " + htmlObj.text()[0:100]
		if htmlObj.text().replace("&nbsp;", " ").strip() == "":
			print "removing blank node in " + htmlObj.text()
			htmlObj.addClass('nukeMe')
		elif htmlObj.hasClass('nukeMe'):
			continue
		else:
			print "exiting blank node loop for " + story['title']
			break

	# keeping images!
	imageCount = 0
	for htmlNode in storyObj.find('img'):

		# making the images local
		# https://gist.github.com/fyears/5575652
		imageUrl = htmlNode.attrib['src']
		imageExt = imageUrl.split('.')[-1]
		imageExt = imageExt.split('/')[0]
		imageDest = "images/" + slugify(story['author']) + "-" + str(imageCount) + "." + imageExt
		download(imageUrl, "output/" + imageDest)
		print("downloading " + imageUrl + " as " + imageDest)
		htmlNode.attrib['src'] = imageDest

		imageCount = imageCount +1

		htmlObj = pq(htmlNode)
		if htmlObj.hasClass('nukeMe'):
			htmlObj.removeClass('nukeMe')

		if htmlObj.parent().hasClass('nukeMe'):
			img = pq(htmlObj).clone()
			htmlObj.parent().before(img)

	storyObj.remove('.nukeMe')


	# we may have stripped the <p> from the front.  ooops.  fixing!
	storyHtmlString = storyObj.html()
	print "checking story start: " + storyHtmlString[0:100]
	if storyHtmlString[0] != "<":
		print "adding in paragraph tag"
		nextParagraphIndex = storyHtmlString.find("<p>")
		storyHtmlString = "<p>" + storyHtmlString[:nextParagraphIndex] + '</p>' + storyHtmlString[nextParagraphIndex:]

	# maybe some day i'll handle their silly line of non-centered asterisks for them.
	#re.search('[a-zA-Z]', the_string)

	htmlOut = htmlOut + storyHtmlString

	footnoteFileName = "footnotes/" + metaData['ShortTitle'] + "/" + story['author'] + ".md"
	print "footnote filename: " + footnoteFileName
	if os.path.isfile(footnoteFileName):
		f = open(footnoteFileName, 'r')
		footnote = f.read().decode("utf8")
		f.close()
		htmlOut = htmlOut + "<hr/>" + markdown.markdown(footnote)

	htmlOut = htmlOut + "</div>"

	return htmlOut



def slugify(str):
	slug = unicodedata.normalize("NFKD",unicode(str)).encode("ascii", "ignore")
	slug = re.sub(r"[^\w]+", " ", slug)
	slug = "-".join(slug.lower().strip().split())
	return slug

def encode_for_xml(unicode_data, encoding='ascii'):
	"""
	Encode unicode_data for use as XML or HTML, with characters outside
	of the encoding converted to XML numeric character references.
	"""
	try:
		return unicode_data.encode(encoding, 'xmlcharrefreplace')
	except ValueError:
		# ValueError is raised if there are unencodable chars in the
		# data and the 'xmlcharrefreplace' error handler is not found.
		# Pre-2.3 Python doesn't support the 'xmlcharrefreplace' error
		# handler, so we'll emulate it.
		return _xmlcharref_encode(unicode_data, encoding)

def _xmlcharref_encode(unicode_data, encoding):
	"""Emulate Python 2.3's 'xmlcharrefreplace' encoding error handler."""
	chars = []
	# Step through the unicode_data string one character at a time in
	# order to catch unencodable characters:
	for char in unicode_data:
		try:
			chars.append(char.encode(encoding, 'strict'))
		except UnicodeError:
			chars.append('&#%i;' % ord(char))
	return ''.join(chars)

def download(url, savepath):
	data = urllib.urlopen(url).read()
	f = file(savepath, 'wb')
	f.write(data)
	f.close()

