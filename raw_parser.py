import re

""" This should
1. read the raw whats app file
2. configure regex to read multi line messages
3. extract messages based on a threshold message length limit
4. create a hash to avoid/merge duplicate messages
"""

## loading data (IOS chat specific)
def startsWithDateAndTime(s):
    #pattern = '^\[([0-9]+)([\/-])([0-9]+)([\/-])([0-9]+)[,]? ([0-9]+):([0-9][0-9]):([0-9][0-9])[ ]?(AM|PM|am|pm)?\]'
    pattern = '^\[([0-9][0-9])([\/-])([0-9][0-9])([\/-])([0-9][0-9])[,]? ([0-9][0-9]):([0-9][0-9]):([0-9][0-9])[ ]?(AM|PM|am|pm)?\]'
    result = re.match(pattern, s)
    if result:
        return True
    return False

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
    splitLine = line.split('] ')
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

def remove_special_char(data):
    acceptable_char = list("0123456789")

    data = ''.join(i for i in data if i in acceptable_char)

    return data

def create_post(date, time, content):

    date = remove_special_char(date)
    time = remove_special_char(time)

    date = list(date)
    date = date[4] + date[5] + date[2] + date[3] + date[0] + date[1]

    with open('post/post-' + date + time + '.md', encoding="utf-8", mode = 'w') as fp:
        fp.write(content)

if __name__ == "__main__":
    parsedData = []
    with open('data/_chat.txt',  encoding="utf-8") as fp:
        messageBuffer = []
        date, time, author = None, None, None
        while True:
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

            temp = list(line)
            if len(temp) > 0:
                print(temp[0])
            if startsWithDateAndTime(line):
                if len(messageBuffer) > 0:
                    parsedData.append([date, time, author, ' '.join(messageBuffer)])
                    messageBuffer.clear()
                date, time, author, message = getDataPoint(line)
                print(time, author, date)
                messageBuffer.append(message)
            else:
                messageBuffer.append('<br>\n')
                messageBuffer.append(line)


    temp = set()
    for itr in parsedData:
        #print(itr[3].encode("utf-8"))
        temp.add(len(itr[3]))
        if len(itr[3]) >= 1000:
            print(itr[3])
            create_post(itr[0], itr[1], itr[3])

