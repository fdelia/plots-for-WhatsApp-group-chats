import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import re

def add(d, key, nr=1):
	if not key in d:
		d[key] = nr
	else:
		d[key] += nr


def countBrackets(text):
	text2 = text.replace(':)', '').replace(';)', '').replace(':-)', '')
	if (text2.count(')') > 0):
		print text2
	add(closedBracketsCount, user, text2.count(')'))
	add(openBracketsCount, user, text2.count('('))


with open("_chat.txt") as f:
    content = f.readlines()

userCount = {}
wordCount = {}
hourCount = {}
imageCount = {}
closedBracketsCount = {}
openBracketsCount = {}
user = None
totalWordCount = 0
for line in content:
	parts = line.split(':', 4)


	if len(parts) == 4: continue # adding someone in the chat

	# add to the predecessor, happens with newlines, is still the same user
	if len(parts) == 1 and parts[0] == '\n': continue
	if len(parts) < 5:
		text = ' '.join(parts)
		words = len(text.split(' '))
		add(wordCount, user, words)
		totalWordCount += words

		countBrackets(text)
		continue

	(date_hour, minute, second, user, text) = parts
	words = len(text.split(' '))
	(date, hour) = date_hour.split(',')
	hour = int(hour)

	user = user.decode('unicode_escape').encode('ascii', 'ignore')
	user = re.sub(' M$', '', user)
	user = user.strip()


	if "<image omitted>\r\n" in text:
		add(imageCount, user)
		continue

	add(userCount, user)
	add(hourCount, hour)
	add(wordCount, user, words)
	totalWordCount += words

	countBrackets(text)




print ("total word count: " + str(totalWordCount))
print(closedBracketsCount)
print(openBracketsCount)

# sort by values
userCountCopy = userCount
userCount = sorted(userCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
wordCount = sorted(wordCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
imageCount = sorted(imageCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
openBracketsCount = sorted(openBracketsCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
# closedBracketsCount = sorted(closedBracketsCount.iteritems(), key=lambda(k, v): (v, k), reverse=True)
# sort by keys
# hourCount = sorted(hourCount.iteritems())


##### NR OF MESSAGES #####
users = [user for (user, count) in userCount if count > 0]
counts = [count for (user, count) in userCount if count > 0]

freq_series = pd.Series.from_array(counts) 
x_labels = users

plt.figure(figsize=(12, 9))
ax = freq_series.plot(kind='bar', color='blue', alpha=0.8)
ax.set_title("# of messages per user in Mensa chat")
ax.set_xlabel("user")
ax.set_ylabel("# of messages")
ax.set_xticklabels(x_labels)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_nr_of_messages.png")


##### WORDS / MESSAGE #####
users = [user for (user, count) in wordCount if userCountCopy[user] > 1]
wordCount2 = [(user, count/userCountCopy[user]) for (user, count) in wordCount if userCountCopy[user] > 1]
wordCount2 = sorted(wordCount2, key=lambda tup: tup[1], reverse=True)

users = [user for (user, count) in wordCount2]
counts = [count for (user, count) in wordCount2]

freq_series = pd.Series.from_array(counts)  
x_labels = users

plt.figure(figsize=(12, 9))
ax = freq_series.plot(kind='bar', color='orange', alpha=0.8)
ax.set_title("Average # of words per message (emoji = 1 word)")
ax.set_xlabel("user")
ax.set_ylabel("# of words")
ax.set_xticklabels(x_labels)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_nr_of_words_per_msg.png")



##### ACTIVITY DURING THE DAY #####
counts = []
for hour in range(0, 24):
	if hour in hourCount:
		counts.append(hourCount[hour])
	else:
		counts.append(0)

freq_series = pd.Series.from_array(counts)
x_labels = range(0, 24)

plt.figure(figsize=(12, 9))
ax = freq_series.plot(kind='bar', color='green', alpha=0.8)
ax.set_title("Chat activity during the day")
ax.set_xlabel("hour")
ax.set_ylabel("# of messages")
ax.set_xticklabels(x_labels)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_activity_per_hour.png")


##### IMAGES SHARED #####
users = [user for (user, count) in imageCount if count > 0]
counts = [count for (user, count) in imageCount if count > 0]

freq_series = pd.Series.from_array(counts) 
x_labels = users

plt.figure(figsize=(12, 9))
ax = freq_series.plot(kind='bar', color='red', alpha=0.8)
ax.set_title("Images shared")
ax.set_xlabel("user")
ax.set_ylabel("# of images")
ax.set_xticklabels(x_labels)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_images_shared.png")



##### BRACKETS #####
users = [user for (user, count) in openBracketsCount if count > 0]
counts = [count for (user, count) in openBracketsCount if count > 0]
counts2 = []
for user in users:
	counts2.append(closedBracketsCount[user])

freq_series = pd.Series.from_array(counts) 
freq_series2 = pd.Series.from_array(counts2)
x_labels = users

plt.figure(figsize=(12, 9))
ax = freq_series.plot(kind='bar', color='blue', alpha=0.8, position=1, width=0.3)
freq_series2.plot(kind='bar', ax=ax, color='magenta', alpha=0.5, position=0, width=0.3)
ax.set_title("Opening / closing brackets")
ax.set_xlabel("user")
ax.set_ylabel("# of brackets")
ax.set_xticklabels(x_labels)

plt.gcf().subplots_adjust(bottom=0.25)
plt.savefig("_brackets.png")

