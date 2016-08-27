import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import re
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
userDateCount = {}
dateCount = OrderedDict()
dateOrder = []
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
	user = re.sub(' M$', '', user) # since Fabio uses ' M' in names
	user = user.strip()


	if "<image omitted>\r\n" in text:
		add(imageCount, user)
		continue

	processText(text)
	
	add(userCount, user)
	add(hourCount, hour)

	add(userDateCount, (user, date))
	add(dateCount, date)
	dateOrder.append(date)




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



##### ACTIVITY OVER TIME #####
dates = dateCount.keys()
x = [datetime.strptime(d, '%d.%m.%y').date() for d in dates]
y = dateCount.values()


# add a user
y2 = []
y3 = []
y4 = []
for date in dates:
	if ('Natalia Malyshewa', date) in userDateCount: y2.append(userDateCount[('Natalia Malyshewa', date) ])
	else: y2.append(0)	

	if ('Squeeeez', date) in userDateCount: y3.append(userDateCount[('Squeeeez', date) ])
	else: y3.append(0)

	if ('Ritish', date) in userDateCount: y4.append(userDateCount[('Ritish', date) ])
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
ax.set_ylabel("# of messages")

for yy in range(min(y), max(y), 100):    
    plt.plot(x, [yy] * len(x), "--", lw=0.5, color="black", alpha=0.3)  

plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.'))
plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=3))
plt.gcf().autofmt_xdate()

plt.plot(x, y, color=tableau20[2], alpha=1)
plt.text(max(x), y[-1], "Total", fontsize=10, color=tableau20[2])    
plt.plot(x, y2, color=tableau20[5], alpha=1)
plt.text(max(x), y2[-1], "Natalia", fontsize=10, color=tableau20[5])    
plt.plot(x, y3, color=tableau20[6], alpha=1)
plt.text(max(x), y3[-1], "Squeeeez", fontsize=10, color=tableau20[6])    
plt.plot(x, y4, color=tableau20[8], alpha=1)
plt.text(max(x), y4[-1], "Ritish", fontsize=10, color=tableau20[8])    

plt.gcf().subplots_adjust(bottom=0.25)
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



##### MESSAGES / USER / TIME #####




