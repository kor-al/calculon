from scraper import Scraper
import pandas as pd

class DataLoader:
    # Compile files if not already compiled
    def compile_files(self):
        my = Scraper()
        my.compile_dialogues('friends')
        my.compile_dialogues('bigbangtheory')
        my.compile_dialogues('house')
        return

    # returns the name of the character and his/her dialogue when a line from script is passed
    def who_said_what(self, dialogue):
        tokens = dialogue.split()
        dialogue = (str)(dialogue).replace(tokens[0]+' ','')
        return (str)(tokens[0]).replace(':',''), dialogue

    # returns complete script on form of a list of lines
    def get_complete_script(self,series):
        with open(series+'.txt') as f:
            scriptLines = f.readlines()
            scriptLines = [x.strip() for x in scriptLines]
        return scriptLines

    # returns pairs of dialogues in a dataframe when the given character from given series is talked to
    def get_conversations_with(self, ourCharacter, series):
        scriptLines = self.get_complete_script(series)
        otherCharactersDialogues = []
        ourCharactersDialogues = []
        previousCharacter, previousCharactersDialogue = self.who_said_what(scriptLines[0])
        for eachLine in scriptLines[1:]:
            currentCharacter, currentCharactersDialogue = self.who_said_what(eachLine)
            if((currentCharacter.lower() == ourCharacter.lower()) and (not currentCharacter == previousCharacter)):
                otherCharactersDialogues.append(previousCharactersDialogue)
                ourCharactersDialogues.append(currentCharactersDialogue)
            previousCharacter = currentCharacter
            previousCharactersDialogue = currentCharactersDialogue
        dataframe = pd.DataFrame({'Others':otherCharactersDialogues,ourCharacter:ourCharactersDialogues})
        return dataframe

    # returns all dialogues in a dataframe spoken by a character in a given series
    def get_all_dialogues(self, ourCharacter, series):
        scriptLines = self.get_complete_script(series);
        ourCharactersDialogues = []
        for eachLine in scriptLines[1:]:
            currentCharacter, currentCharactersDialogue = self.who_said_what(eachLine)
            if(currentCharacter.lower() == ourCharacter.lower()):
                ourCharactersDialogues.append(currentCharactersDialogue)
        dataframe = pd.DataFrame({ourCharacter:ourCharactersDialogues})
        return dataframe