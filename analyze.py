import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re


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

def processText(text):
	global totalWordCount

	words = len(text.split(' '))
	add(wordCount, user, words)
	totalWordCount += words

	for word in text.split(' '):
		word = re.sub(r'[\(\)\"\.,:?]*', '', word.lower()).strip()
		if word == '': continue
		add(singlewordCount, word)

	countBrackets(text)


with open("_chat.txt") as f:
    content = f.readlines()


userCount = {}
wordCount = {}
singlewordCount = {}
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
		processText(text)
		continue

	(date_hour, minute, second, user, text) = parts
	(date, hour) = date_hour.split(',')
	hour = int(hour)

	user = user.decode('unicode_escape').encode('ascii', 'ignore')
	user = re.sub(' M$', '', user)
	user = user.strip()


	if "<image omitted>\r\n" in text:
		add(imageCount, user)
		continue

	processText(text)
	
	add(userCount, user)
	add(hourCount, hour)





print ("total word count: " + str(totalWordCount))

# sort by values
userCountCopy = userCount
userCount = sorted(userCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
wordCount = sorted(wordCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
imageCount = sorted(imageCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
openBracketsCount = sorted(openBracketsCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
singlewordCount = sorted(singlewordCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)


##### NR OF MESSAGES #####
users = [user for (user, count) in userCount if count > 0]
counts = [count for (user, count) in userCount if count > 0]

freq_series = pd.Series.from_array(counts) 
plt.figure(figsize=(12, 9))

ax = freq_series.plot(kind='bar', color=tableau20[0], alpha=0.8)
ax.spines["top"].set_visible(False)    
ax.spines["right"].set_visible(False)    
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()
ax.set_title("# of messages per user in Mensa chat")
ax.set_xlabel("user")
ax.set_ylabel("# of messages")
ax.set_xticklabels(users)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_nr_of_messages.png", bbox_inches="tight")


##### WORDS / MESSAGE #####
users = [user for (user, count) in wordCount if userCountCopy[user] > 1]
wordCount2 = [(user, count/userCountCopy[user]) for (user, count) in wordCount if userCountCopy[user] > 1]
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
ax.set_title("Average # of words per message (emoji = 1 word)")
ax.set_xlabel("user")
ax.set_ylabel("# of words")
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
ax.set_ylabel("# of messages")
ax.set_xticklabels(range(0, 24))

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_activity_per_hour.png", bbox_inches="tight")


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
ax.set_xlabel("user")
ax.set_ylabel("# of images")
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
ax.set_xlabel("user")
ax.set_ylabel("# of brackets")
ax.set_xticklabels(users)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_brackets.png", bbox_inches="tight")



##### WORDS #####
# print(' ')
# for (word, count) in singlewordCount:
# 	print( str(word) + " \t\t " + str(count))




