import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import pandas as pd
import re
import json
import copy
from collections import OrderedDict
from datetime import datetime


# These are the "Tableau 20" colors as RGB.    
tableau20 = [(31, 119, 180), (174, 199, 232), (255, 127, 14), (255, 187, 120),    
             (44, 160, 44), (152, 223, 138), (214, 39, 40), (255, 152, 150),    
             (148, 103, 189), (197, 176, 213), (140, 86, 75), (196, 156, 148),    
             (227, 119, 194), (247, 182, 210), (127, 127, 127), (199, 199, 199),    
             (188, 189, 34), (219, 219, 141), (23, 190, 207), (158, 218, 229)]    
  
# Scale the RGB values to the [0, 1] range, which is the format matplotlib accepts.    
for i in range(len(tableau20)):    
    r, g, b = tableau20[i]    
    tableau20[i] = (r / 255., g / 255., b / 255.)    



def add(d, key, nr=1):
	if not key in d:
		d[key] = nr
	else:
		d[key] += nr


def countBrackets(text):
	text2 = text.replace(':)', '').replace(';)', '').replace(':-)', '')
	# if (text2.count(')') > 0):
	# 	print text2
	add(closedBracketsCount, user, text2.count(')'))
	add(openBracketsCount, user, text2.count('('))

def countEmojis(text):
	emoticons = re.finditer(r'[\U0001f600-\U0001f650]', text)
	count = sum(1 for _ in emoticons)
	# print count
	return count

def processText(text, user):
	global totalWordCount


	words = len(text.split(' '))
	add(wordCount, user, words)
	totalWordCount += words

	# text = re.sub(r"(\.)+", ".", text)
	sentences = len(text.split('. '))
	add(userSentenceCount, user, sentences)

	for word in text.split(' '):
		word = re.sub(r'[\(\)\"\.,:?]*', '', word.lower()).strip()
		if word == '': continue
		add(singlewordCount, word)

		if not user in userSinglewordCount: userSinglewordCount[user] = {}
		add(userSinglewordCount[user], word)
		# if user == POPULARITY_USER: add(userSinglewordCount, word)

	countBrackets(text)


with open("_chat.txt") as f:
    content = f.readlines()
    f.close()

userMsgCount = {}
userDateCount = {}
userSentenceCount = {}
dateCount = OrderedDict()
dateOrder = []
wordCount = {}
singlewordCount = {}
userSinglewordCount = {}
hourCount = {}
imageCount = {}
closedBracketsCount = {}
openBracketsCount = {}
totalWordCount = 0
user = None
for line in content:
	parts = line.split(':', 4)


	# TODO add b/c of Wendy:
	# /(([a-z']\s)*[a-z\.]+)/ig

	if len(parts) == 4: continue # adding someone in the chat

	# add to the predecessor, happens with newlines, is still the same user
	if len(parts) == 1 and parts[0] == '\n': continue
	if len(parts) < 5:
		text = ' '.join(parts)
		processText(text, user)
		continue

	(date_hour, minute, second, user, text) = parts
	(date, hour) = date_hour.split(',')
	hour = int(hour)

	user = user.decode('unicode_escape').encode('ascii', 'ignore')
	user = re.sub(' M$', '', user) # since Fabio uses ' M' in names
	user = user.split()[0] # unicode problem
	user = user.strip()


	if "<image omitted>\r\n" in text:
		add(imageCount, user)
		continue

	processText(text, user)
	
	add(userMsgCount, user)
	add(hourCount, hour)

	add(userDateCount, (user, date))
	add(dateCount, date)
	dateOrder.append(date)




print ("total word count: " + str(totalWordCount))

# sort by values
userMsgCountCopy = userMsgCount
userMsgCount = sorted(userMsgCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
wordCount = sorted(wordCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
imageCount = sorted(imageCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
openBracketsCount = sorted(openBracketsCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
singlewordCount = sorted(singlewordCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
# userSinglewordCount = sorted(userSinglewordCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
for user, w in userSinglewordCount.iteritems():
	userSinglewordCount[user] = sorted(userSinglewordCount[user].iteritems(), key=lambda(k, v): (v, k), reverse=True)


##### NR OF MESSAGES #####
users = [user for (user, count) in userMsgCount if count > 0]
counts = [count for (user, count) in userMsgCount if count > 0]

freq_series = pd.Series.from_array(counts) 
plt.figure(figsize=(12, 9))

ax = freq_series.plot(kind='bar', color=tableau20[0], alpha=0.8)
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_title("Amount of messages per user")
ax.set_xlabel("User")
ax.set_ylabel("Amount of messages")
ax.set_xticklabels(users)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_nr_of_messages.png", bbox_inches="tight")


##### WORDS / MESSAGE #####
users = [user for (user, count) in wordCount if userMsgCountCopy[user] > 1]
wordCount2 = [(user, count/userMsgCountCopy[user]) for (user, count) in wordCount if userMsgCountCopy[user] > 1]
wordCount2 = sorted(wordCount2, key=lambda tup: tup[1], reverse=True)

users = [user for (user, count) in wordCount2]
counts = [count for (user, count) in wordCount2]

freq_series = pd.Series.from_array(counts)  
plt.figure(figsize=(12, 9))

ax = freq_series.plot(kind='bar', color=tableau20[1], alpha=0.8)
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_title("Average amount of words per message (emoji = 1 word)")
ax.set_xlabel("User")
ax.set_ylabel("Amount of words")
ax.set_xticklabels(users)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_nr_of_words_per_msg.png", bbox_inches="tight")



##### ACTIVITY DURING THE DAY #####
counts = []
for hour in range(0, 24):
	if hour in hourCount:
		counts.append(hourCount[hour])
	else:
		counts.append(0)

freq_series = pd.Series.from_array(counts)
plt.figure(figsize=(12, 9))

ax = freq_series.plot(kind='bar', color=tableau20[2], alpha=0.8)
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_title("Chat activity during the day")
ax.set_xlabel("hour")
ax.set_ylabel("Amount of messages")
ax.set_xticklabels(range(0, 24))

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_activity_per_hour.png", bbox_inches="tight")



##### ACTIVITY OVER TIME #####
dates = dateCount.keys()
x = [datetime.strptime(d, '%d.%m.%y').date() for d in dates]
y = dateCount.values()


# add a user
# TODO make this simpler
y2 = []
y3 = []
y4 = []
for date in dates:
	if ('Fabio', date) in userDateCount: y2.append(userDateCount[('Fabio', date) ])
	else: y2.append(0)	

	if ('Anna', date) in userDateCount: y3.append(userDateCount[('Anna', date) ])
	else: y3.append(0)

	if ('Efrem', date) in userDateCount: y4.append(userDateCount[('Efrem', date) ])
	else: y4.append(0)	


plt.figure(figsize=(12, 9))
ax = plt.subplot(111)    

ax.spines["top"].set_visible(False)    
ax.spines["bottom"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.spines["left"].set_visible(False)   
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_title("Chat activity per date (total and top users)")
ax.set_xlabel("date")
ax.set_ylabel("Amount of messages")

y = y2 # when Total is disabled
for yy in range(min(y), max(y), 100):    
    plt.plot(x, [yy] * len(x), "--", lw=0.5, color="black", alpha=0.3)  

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=50))
plt.gcf().autofmt_xdate()

ax = plt.gca()
# plt.plot(x, y, color=tableau20[2], alpha=1, label="Total")
# plt.text(max(x), y[-1], "Total", fontsize=10, color=tableau20[2])    
ax.plot(x, y2, color=tableau20[5], alpha=1, label="Fabio")
# plt.text(max(x), y2[-1], "Fabio", fontsize=10, color=tableau20[5])    
ax.plot(x, y3, color=tableau20[6], alpha=1, label="Anna")
# plt.text(max(x), y3[-1], "Anna", fontsize=10, color=tableau20[6])    
ax.plot(x, y4, color=tableau20[8], alpha=1, label="Efrem")
# plt.text(max(x), y4[-1], "Efrem", fontsize=10, color=tableau20[8])    

plt.gcf().subplots_adjust(bottom=0.25)
ax.legend(loc='upper left', shadow=True)
plt.savefig("_activity_over_time.png", bbox_inches="tight")



##### IMAGES SHARED #####
users = [user for (user, count) in imageCount if count > 0]
counts = [count for (user, count) in imageCount if count > 0]

freq_series = pd.Series.from_array(counts) 
plt.figure(figsize=(12, 9))

ax = freq_series.plot(kind='bar', color=tableau20[12], alpha=0.8)
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_title("Images shared")
ax.set_xlabel("User")
ax.set_ylabel("Amount of images")
ax.set_xticklabels(users)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_images_shared.png", bbox_inches="tight")



##### BRACKETS #####
users = [user for (user, count) in openBracketsCount if count > 0]
counts = [count for (user, count) in openBracketsCount if count > 0]
counts2 = []
for user in users:
	counts2.append(closedBracketsCount[user])

freq_series = pd.Series.from_array(counts) 
freq_series2 = pd.Series.from_array(counts2)

plt.figure(figsize=(12, 9))
ax = freq_series.plot(kind='bar', color=tableau20[18], alpha=0.8, position=1, width=0.3)
freq_series2.plot(kind='bar', ax=ax, color=tableau20[2], alpha=0.8, position=0, width=0.3)
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_title("Opening / closing brackets")
ax.set_xlabel("User")
ax.set_ylabel("Amount of brackets")
ax.set_xticklabels(users)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_brackets.png", bbox_inches="tight")



##### WORDS #####
# print(' ')
# for (word, count) in singlewordCount:
# 	print( str(word) + " \t\t " + str(count))




##### WORD "CLOUD" PLOT #####
wordsToPlotOrg = {}
max_y = 0
for word, count in singlewordCount[:20]:
	wordsToPlotOrg[word] = {}
	wordsToPlotOrg[word]['y'] = float(count) / totalWordCount
	wordsToPlotOrg[word]['x'] = 0
	max_y = max(max_y, float(count) / totalWordCount)




# handles = []
for POPULARITY_USER in users:
	plt.figure(figsize=(12, 12))
	wordCountThisUser = 0
	max_x = 0
	wordsToPlot = {}
	wordsToPlot = copy.deepcopy(wordsToPlotOrg)

	# get word count for current user
	for user, count in wordCount:
		if user == POPULARITY_USER:
			wordCountThisUser = count
			break

	# set coordinates 
	for word, count in userSinglewordCount[POPULARITY_USER][:20]:
		if word not in wordsToPlot: wordsToPlot[word] = {}
		wordsToPlot[word]['x'] = float(count) / wordCountThisUser
		max_x = max(max_x, float(count) / wordCountThisUser)
		if 'y' not in wordsToPlot[word]: 
			wordsToPlot[word]['y'] = 0
			# print word

	# plot
	for word, xy in wordsToPlot.iteritems():
		word = word.decode('unicode_escape').encode('ascii', 'ignore')
		plt.text(xy['x'], xy['y'], word, ha='center', va='center', color=tableau20[0], size=10, label=POPULARITY_USER)

	POPULARITY_USER = POPULARITY_USER.decode('utf-8')
	# handles.append(mpatches.Patch(color=tableau20[color_i], label=POPULARITY_USER))

	ax = plt.gca()
	ax.set_title("Popularity (use) of words")
	plt.plot([0, 1], [0, 1], "--", lw=0.5, color="black", alpha=0.3)  
	plt.xlabel("Popularity " + POPULARITY_USER)
	plt.ylabel("Popularity in chat")
	plt.axis([0, max_x*1.05, 0, max_y*1.05])
	plt.xticks([])
	plt.yticks([])

	# plt.legend(handles = handles, loc='upper left')
	plt.savefig("_words_popularity_" + POPULARITY_USER + ".png", bbox_inches="tight")
	# plt.savefig("_words_popularity.png", bbox_inches="tight")

'''
with open('_words_popularity_all_users.txt', 'w') as outfile:
	json.dump(userSinglewordCount, outfile)
	outfile.close()
'''


##### AMOUNT OF MESSAGES / AVERAGE SENTENCE LENGTH FOR SOME USERS #####
usersToPlot = {}
for (user, count) in wordCount:
	if user not in userSentenceCount: continue
	if userMsgCountCopy[user] < 10: continue
	usersToPlot[user] = {
		'msgs': userMsgCountCopy[user],
		'sentcL': float(count) / userSentenceCount[user]
	}

plt.figure(figsize=(12, 12))
max_x = 0
max_y = 0
min_y = 999999999
color_i = 0
for user, content in usersToPlot.iteritems():
	plt.text(content['msgs'], content['sentcL'], user, ha='center', va='center', color=tableau20[color_i], size=12)
	max_x = max(max_x, content['msgs'])
	max_y = max(max_y, content['sentcL'])
	min_y = min(min_y, content['sentcL'])
	color_i += 1
	if color_i == 20: color_i = 0 

# plt.plot([0, max_x], [0, max_y], "--", lw=0.5, color="black", alpha=0.3)  
ax = plt.gca()
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()


plt.xlabel("Amount of messages")
plt.ylabel("Average amount of words / sentence")
plt.axis([0, max_x*1.1, min_y*0.9, max_y*1.05])
plt.savefig("_msgs_vs_sentence_length.png", bbox_inches="tight")



##### AMOUNT OF "THE" / AVERAGE SENTENCE LENGTH FOR SOME USERS #####
THE_WORD = 'and'
usersToPlot = {}
for (user, count) in wordCount:
	if user not in userSinglewordCount: continue
	if user not in userSentenceCount: continue
	if userMsgCountCopy[user] < 20: continue

	theCount = 0
	for word, count2 in userSinglewordCount[user]:
		if word == THE_WORD:
			theCount = count2
			break

	usersToPlot[user] = {
		'sentl': float(count) / userSentenceCount[user],
		'amount': float(theCount) / count
	}


plt.figure(figsize=(12, 9))
max_x = 0
max_y = 0
min_x = 99999999999
min_y = 99999999999
color_i = 0
for user, content in usersToPlot.iteritems():
	plt.text(content['sentl'], content['amount'], user, ha='center', va='center', color=tableau20[color_i], size=12)
	max_x = max(max_x, content['sentl'])
	max_y = max(max_y, content['amount'])
	min_x = min(min_x, content['sentl'])
	min_y = min(min_y, content['amount'])
	color_i += 1
	if color_i == 20: color_i = 0 

# plt.plot([0, max_x], [0, max_y], "--", lw=0.5, color="black", alpha=0.3)  
ax = plt.gca()
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)  
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()


plt.xlabel("Average amount of words / sentence")
plt.ylabel("Use of '"+THE_WORD+"'")
plt.axis([min_x*0.9, max_x*1.1, min_y*0.9, max_y*1.05])
plt.savefig("_sent_length_vs_word.png", bbox_inches="tight")


