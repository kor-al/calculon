# import libraries
from urllib.request import urlopen
from bs4 import BeautifulSoup

def is_Dialog(text):
    tokens = text.split()
    if(len(tokens)>0):
        if (tokens[0].__contains__(':') and not tokens[0]=='Scene:'):
            return True;
        else:
            return False;
    return False;

# get list of all urls for given series
def get_URLs_episodes(series):
    if(series == 'friends'):
        main_page = 'http://www.livesinabox.com/friends/scripts.shtml'
        main_source = urlopen(main_page)
        main_soup = BeautifulSoup(main_source, 'html.parser')
        all_episodes_urls = []
        rootURL = 'http://www.livesinabox.com/friends/'
        unorderedList = main_soup.find_all("ul")
        for eachList in unorderedList:
            for eachItem in eachList.find_all('li'):
                a = eachItem.find('a')
                eachURL = rootURL+a['href']
                all_episodes_urls.append(eachURL)

    elif(series == 'bigbangtheory'):
        main_page = 'https://bigbangtrans.wordpress.com/'
        main_source = urlopen(main_page)
        main_soup = BeautifulSoup(main_source, 'html.parser')
        all_episodes_urls = []
        allLists = main_soup.find_all("li")
        notAnEpisodeURL = 'https://bigbangtrans.wordpress.com/about/'
        for eachItem in allLists:
            a = eachItem.find('a')
            eachURL =  a['href']
            if(not eachURL == notAnEpisodeURL):
                all_episodes_urls.append(eachURL)

    return all_episodes_urls;

def extract_dialogues(episodeURL):
    page_source = urlopen(episodeURL)
    episode_soup = BeautifulSoup(page_source, 'html.parser')
    episode_dialogues = []
    lines=episode_soup.find_all("p")
    for line in lines:
        grabbed_text=str(line.text)
        if(is_Dialog(grabbed_text)):
            # replace \n with spaces
            grabbed_text = grabbed_text.replace('\n', ' ')
            episode_dialogues.append(grabbed_text)
    return episode_dialogues;

# get dialogues for series given as option and compile a file
# Possible inputs: 'friends', 'bigbangtheory'
def compile_dialogues(series):
    if(series == 'friends'):
        outputFile = open('friends.txt','w')
        listURLs = get_URLs_episodes(series)
        for eachURL in listURLs:
            for eachDialog in extract_dialogues(eachURL):
                outputFile.write(eachDialog+'\n')

    elif(series == 'bigbangtheory'):
        outputFile = open('bigbangtheory.txt', 'w')
        listURLs = get_URLs_episodes(series)
        for eachURL in listURLs:
            for eachDialog in extract_dialogues(eachURL):
                outputFile.write(eachDialog + '\n')

#compile_dialogues('friends')
#compile_dialogues('bigbangtheory')