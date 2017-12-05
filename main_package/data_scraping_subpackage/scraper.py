# import libraries
from urllib.request import urlopen
from bs4 import BeautifulSoup, NavigableString, Tag
import os

class Scraper:
    def is_Dialog(self,text):
        tokens = text.split()
        if(len(tokens)>0):
            if (tokens[0].__contains__(':') and not tokens[0]=='Scene:'):
                return True;
            else:
                return False;
        return False;

    # get list of all urls for given series. Possible options: 'friends', 'bigbangtheory', 'house'
    def get_URLs_episodes(self, series):
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

        elif(series == 'house'):
            main_page = 'https://clinic-duty.livejournal.com/12225.html'
            main_source = urlopen(main_page)
            main_soup = BeautifulSoup(main_source, 'html.parser')
            all_episodes_urls = []
            divContainer = main_soup.find('div', attrs={'class': 'entryText s2-entrytext '})
            for all_a_tags in divContainer.find_all('a'):
                # an observation in html to make things work
                if ((str)(all_a_tags['href']).__contains__('html')):
                    all_episodes_urls.append(all_a_tags['href'])

        return all_episodes_urls;

    # extract dialogues from the given series. episode url is given along with series name: 'friends', 'bigbangtheory', 'house'
    def extract_dialogues(self, episodeURL, series):
        episode_dialogues = []
        if(series == 'friends' or series == 'bigbangtheory'):
            page_source = urlopen(episodeURL)
            episode_soup = BeautifulSoup(page_source, 'html.parser')
            lines=episode_soup.find_all("p")
            for line in lines:
                grabbed_text=str(line.text)
                if(self.is_Dialog(grabbed_text)):
                    # replace \n with spaces
                    grabbed_text = grabbed_text.replace('\n', ' ')
                    episode_dialogues.append(grabbed_text)
            return episode_dialogues;
        elif(series == 'house'):
            page_source = urlopen(episodeURL)
            episode_soup = BeautifulSoup(page_source, 'html.parser')
            allText = episode_soup.find('div', attrs={'class': 'entryText s2-entrytext '})
            # special logic to pick text between br tags
            for br in allText.findAll('br'):
                next_s = br.nextSibling
                if not (next_s and isinstance(next_s, NavigableString)):
                    continue
                next2_s = next_s.nextSibling
                if next2_s and isinstance(next2_s, Tag) and next2_s.name == 'br':
                    text = str(next_s).strip()
                    if text:
                        if (self.is_Dialog(next_s)):
                            episode_dialogues.append(next_s)

            return episode_dialogues

        print('Could not find any dialogues')
        return episode_dialogues

    # get dialogues for series given as option and compile a file
    # Possible inputs: 'friends', 'bigbangtheory'
    def compile_dialogues(self, series):
        if not os.path.isfile(series+'.txt'):
            if(series == 'friends' or series == 'bigbangtheory'):
                outputFile = open(series+'.txt','w')
                listURLs = self.get_URLs_episodes(series)
                for eachURL in listURLs:
                    for eachDialog in self.extract_dialogues(eachURL,series):
                        outputFile.write(eachDialog+'\n')
            # BEWARE: the website blocks you after multiple attempts to scrape data
            elif(series == 'house'):
                outputFile = open(series+'.txt', 'w')
                listURLs = self.get_URLs_episodes(series);
                listURLs1 = listURLs[0:90]
                for eachURL in listURLs1:
                    for eachDialog in self.extract_dialogues(eachURL,series):
                        outputFile.write(eachDialog + '\n')
                listURLs2 = listURLs[90:]
                for eachURL in listURLs2:
                    for eachDialog in self.extract_dialogues(eachURL,series):
                        outputFile.write(eachDialog + '\n')
        else:
            print('File', series+'.txt', 'already exists. Please delete it if you want to generate it again')