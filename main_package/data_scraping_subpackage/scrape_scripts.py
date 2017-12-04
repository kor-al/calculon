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

def get_URLs_friends_episodes():
    # specify the url
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
            #print(all_episodes_urls)
    return all_episodes_urls;

def extract_friends_dialogues(episodeURL):
    # query the website and return the html to the variable ‘page_source’
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
    #print(episode_dialogues)
    return episode_dialogues;

# get dialogues from all seasons and write to friends.txt
def compile_friends_dialogues():
    outputFile = open('friends.txt','w')
    # get a list of all URLs
    listURLs = get_URLs_friends_episodes()
    # get dialogues for each episode and write to a file
    for eachURL in listURLs:
        for eachDialog in extract_friends_dialogues(eachURL):
            outputFile.write(eachDialog+'\n')

#compile_friends_dialogues()