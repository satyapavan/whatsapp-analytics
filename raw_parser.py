# Python program to find the k most frequent words
# from data set
from collections import Counter

from confidentiality_clause import CC_SECRETS

from difflib import SequenceMatcher

## For regex
import re
## For avoiding a-z, A-Z, 0-9 and punctuation typing
import string

""" This should
1. read the raw whats app file
2. configure regex to read multi line messages
3. extract messages based on a threshold message length limit
4. create a hash to avoid/merge duplicate messages
"""

POST_COUNTER = 1
parsedData = []


## loading data (IOS chat specific)
def startsWithDateAndTime(s):
    """
    ## iOS 24h format
    [21/02/19, 09:01:59] FName LName: Haha yes.
    ## Android 12h format
    30/06/16, 11:26 am - FName LName: Very Good
    """

    #pattern = '^\[([0-9]+)([\/-])([0-9]+)([\/-])([0-9]+)[,]? ([0-9]+):([0-9][0-9]):([0-9][0-9])[ ]?(AM|PM|am|pm)?\]'
    #pattern = '^\[([0-9][0-9])([\/-])([0-9][0-9])([\/-])([0-9][0-9])[,]? ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])[ ]?(AM|PM|am|pm)?\]'
    pattern = '^[\[]?\d{2}(\/)\d{2}(\/)\d{2}(, )\d{1,2}(\:)\d{2}(((\:)\d{2})[\]]|([ ](AM|PM|am|pm)))'
    result = re.match(pattern, s)
    if result:
        return True
    return False

def convert_date_ddmmyy_to_yyyymmdd(date):
    date = list(date)
    date = '20' + date[4] + date[5] + '-' + date[2] + date[3] + '-' + date[0] + date[1]
    return date

def sort_content():
    global parsedData

    ## Usually this doESn"t need a function by iteself. BUT SINCE WE ARE GOING TO USE A FANCY IMplementAtion< this would be needing one

    for itr in parsedData:
        print(f'BEFORE Printing {itr[0]}')
    parsedData.sort(key = lambda itr : convert_date_ddmmyy_to_yyyymmdd(remove_special_char(itr[0])))
    for itr in parsedData:
        print(f'AFTER Printing {itr[0]}')


def clear_dups():
    global parsedData


    ### Simpler way to remove dups, just create a key with the content and boom!

    get_unique_dict = {}

    for data in parsedData:
        if data[3] not in get_unique_dict.keys():
            get_unique_dict[data[3]] = data

    parsedData.clear()

    for k, v in get_unique_dict.items():
        parsedData.append(v)

    print(f'Length after dict check: {len(parsedData)}')

    return

    unique_ParsedData = []

    print(len(parsedData), len(unique_ParsedData))

    ### CPU intensive way by looping n^2 times to find dups ;-)

    for outerItr in range(len(parsedData)):
        is_dup = False
        for innerItr in range(len(unique_ParsedData)):
            print(f'Outer{outerItr} - Inner{innerItr} - Length{len(parsedData)}')
            if SequenceMatcher(None, parsedData[outerItr][3], unique_ParsedData[innerItr][3]).quick_ratio() >= float(0.9):
                is_dup = True
                print("DUPSSS")
                print(parsedData[outerItr][3], unique_ParsedData[innerItr][3])
                break

        if not is_dup:
            unique_ParsedData.append(parsedData[outerItr])
        else:
            print("Duplicate found")

    parsedData.clear()
    parsedData = unique_ParsedData


def identify_delimiter(data):

    ## 30/06/16, 11:26 am - FName LName: Very Good
    pattern = '^\d{2}(\/)\d{2}(\/)\d{2}(, )\d{1,2}(\:)\d{2}[ ]?(AM|PM|am|pm)?'
    result = re.match(pattern, data)
    if result:
        return "- "

    ## [21/02/19, 09:01:59] FName LName: Haha yes.
    pattern = '^[\[]\d{2}(\/)\d{2}(\/)\d{2}(, )\d{2}(\:)\d{2}((\:)\d{2})[\]]'
    result = re.match(pattern, data)
    if result:
        return "] "

def is_confidentiality_clause(data):
    for token in CC_SECRETS:
        if re.search(token, data, re.IGNORECASE):
            return False

    return True

def tag_finder(data):
    keys = ['finance', 'financial', 'money', 'joke', 'boss', 'fake', 'news', 'covid', 'mother', 'mom', 'husband', 'dad', 'father', 'love', 'marriage', 'wife', 'scam', 'fraud', 'password', 'atm', 'sms']
    tags = []

    data = data.lower()

    for key in keys:
        if data.find(key) > -1:
            tags.append(key)

    for word in data.split():
        if word[0] == '#':
            string.digits
            if len(''.join(i for i in word if i not in list(string.digits + string.punctuation))) >= 2:
                tags.append(word)

    return tags


def FindAuthor(s):
    patterns = [
        '([\w]+):',                        # First Name
        '([\w]+[\s]+[\w]+):',              # First Name + Last Name
        '([\w]+[\s]+[\w]+[\s]+[\w]+):',    # First Name + Middle Name + Last Name
        '([+]\d{2} \d{5} \d{5}):',         # Mobile Number (India)
        '([+]\d{1} \d{3} \d{3} \d{4}):',   # Mobile Number (US),
        '\(?\d{3}\)?-? *\d{3}-? *-?\d{4}', # Mobile Number (US),
        '([\w]+)[\u263a-\U0001f999]+:',    # Name and Emoji
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False

def getDataPoint(line):
    splitLine = line.split(identify_delimiter(line))
    dateTime = splitLine[0]
    if ',' in dateTime:
        date, time = dateTime.split(',')
    else:
        date, time = dateTime.split(' ')
    message = ' '.join(splitLine[1:])
    if FindAuthor(message):
        splitMessage = message.split(': ')
        author = splitMessage[0]
        message = ' '.join(splitMessage[1:])
    else:
        author = None
    return date, time, author, message

def identify_language(data):
    ## One simple way to identify the language is remove all the english alphabets and see if the count of characters reduced
    eng_char = list(string.ascii_lowercase + string.ascii_uppercase )

    len_v1 = len(data)
    data = ''.join(i for i in data if i not in eng_char)
    len_v2 = len(data)

    if (len_v2/len_v1)*100 >= 50:
        return 'telugu'
    else:
        return 'english'

def remove_special_char(data):
    acceptable_char = list(string.digits)

    data = ''.join(i for i in data if i in acceptable_char)

    return data

def generate_title(data):
    return 'Post-' + '%04d' % POST_COUNTER
    data = data.replace('<br>', ' ').replace('\n', ' ').replace('\r', ' ').replace('*', ' ')

    ## This will remove all the double and triple spaces and replaec them with a single space
    data = ' '.join(data.split())
    ## truncating by 30 is creating abruptly ended words, not looking good
    ## so lets look for the first space after 30 and then truncate till there
    return data[0:data.find(' ', 30)]

def create_post(date, time, content):

    date = remove_special_char(date)
    time = remove_special_char(time)

    date = convert_date_ddmmyy_to_yyyymmdd(date)

    global POST_COUNTER
    with open('post/' + date + '-' + 'P' + '%04d'%POST_COUNTER + '.md', encoding="utf-8", mode = 'w') as fp:
        header = []
        header.append('---')
        header.append('\n')
        header.append('layout: post')
        header.append('\n')
        header.append('title: ' + generate_title(content))
        #header.append('title: ' + date + ' ' + time)
        header.append('\n')
        header.append('author: sal')
        header.append('\n')
        header.append('image: assets/images/' + '%04d'%POST_COUNTER + '.jpg')
        header.append('\n')
        header.append('categories: [' + identify_language(content) + ']')
        header.append('\n')
        header.append('tags: ' + str(tag_finder(content)))
        header.append('\n')
        header.append('---')
        header.append('\n')

        fp.writelines(header)
        fp.write(content)

        POST_COUNTER += 1

def process_file(file_name):
    global parsedData
    with open(file_name, encoding="utf-8") as fp:
        messageBuffer = []
        date, time, author = None, None, None
        while True:
            print("---------------------------------------------------------")

            line = fp.readline()

            if not line:
                break;

            """
            You have a U+200E LEFT-TO-RIGHT MARK character in your input. 
            It's a non-printing typesetting directive, instructing anything that is displaying the text to switch to left-to-right mode. 
            The string, when printed to a console that is already set to display from left-to-right (e.g. the vast majority of terminals in the western world), 
                will not look any different from one printed without the marker.

            Since it is not part of the date, you could just strip such characters:
                Hence we are stripping the u200e char. This is coming for WhatsApp notifications, like desc change, profile pic change etc.
            """
            line = line.strip().strip("\u200e")

            print(line)

            if startsWithDateAndTime(line):
                if len(messageBuffer) > 0:
                    parsedData.append([date, time, author, ' '.join(messageBuffer)])
                    messageBuffer.clear()
                date, time, author, message = getDataPoint(line)
                print(f"Time: {time}, author:{author}, date:{date}")
                messageBuffer.append(message)
            else:
                messageBuffer.append(' <br>\n')
                messageBuffer.append(line)

## https://stackoverflow.com/questions/27327303/10-most-frequent-words-in-a-string-python

if __name__ == "__main__":
    files = ['data/mls-sh.txt', 'data/mls-qk.txt']
    for file in files:
        process_file(file)

    tempParsedData = []
    print(f'Length before len check: {len(parsedData)}')
    for itr in parsedData:
        if len(itr[3]) >= 3000:
            tempParsedData.append(itr)
            print(f'NOT Removing {len(itr[3])} - {itr[3]}')

    parsedData.clear() 
    parsedData = tempParsedData

    for itr in parsedData:
        print(f'AFTER DELETING 3000: {len(itr[3])} - {itr}')

    print(f'Length after len check: {len(parsedData)}')
    clear_dups()
    print(f'Length after dups check: {len(parsedData)}')

    ### Now that we have put the data into keys and sorted them by content, lets sort them back using timestamps
    sort_content()

    for itr in parsedData:
        #print(itr[3].encode("utf-8"))
        if len(itr[3]) >= 3000:
            print(itr[3])
            if is_confidentiality_clause(itr[3]):
                create_post(itr[0], itr[1], itr[3])
