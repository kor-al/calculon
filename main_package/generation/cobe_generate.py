import cobe
import re
from cobe.brain import Brain
import nltk
import string
from nltk.tokenize.moses import MosesDetokenizer, MosesTokenizer
import math
from collections import Counter
import random
import language_check
import os.path

def read_file(file):
    print("- Reading file ", file)
    file_raw = None
    with open(file, 'r', encoding='utf8') as f:
        file_raw = f.read()
    file_raw = re.sub(r'\s+', ' ', file_raw)
    return file_raw
    
def sanitize(token_list):
    """
    Sanitize tokens:
    - Words consisting only of letters and '-' are considered as 'words'.
    - Numbers and words with apostrophes are also good
    - Save all the punctuation
    :param token_list: original list of tokens
    :return: sanitized list of tokens
    """

    is_word = re.compile(r'(^[a-zA-Z]*$)|(^[0-9]+$)|(^(?=.*\w)^(\w|\'\w)+$)|(^(&apos;)(\w)+$)|(^\w+(?:-\w+)+$)')
    #words, numbers, words with an apostrophes and dashes
    return [token for token in token_list if (is_word.match(token) and token not in '_"') or token in '.?!-:,']# + ['.']    

def delete_parenthesis(text):
    return '\n'.join([re.sub("[\(\[].*?[\)\]]", "", s) for s in  text.split('\n')])

def clean_text(raw_text, get_questions = False):
    """
    Words consist of letters or numbers
    :param raw_text: text (not divided into sentences)
    :return: list of sanitized sentences
    """
    # Tokenize text into sentences.
    raw_text = delete_parenthesis(raw_text)

    sentences = nltk.sent_tokenize(raw_text)

    #Tokenize each sentence
    sanitized_sentences = []
    for s in sentences:
        #use Moses instead of nltk.word_tokenize(s)  - better with apostrophes: cant -> (can + 't) but not (ca + 'n't)
        tokenizer = MosesTokenizer()
        s_tokens = tokenizer.tokenize(s)
        #s_tokens = nltk.word_tokenize(s)
        if (not get_questions and s_tokens[-1]!='?') or (get_questions and s_tokens[-1] == '?'):
            sanitized_sentences.append(sanitize(s_tokens))

    #Sanitized tokens joined using detokenizer
    detokenizer = MosesDetokenizer()
    return [detokenizer.detokenize(s, return_str=True) for s in sanitized_sentences]

def learn_text(text, brain_name):
    brain = Brain(brain_name)
    if not os.path.isfile(brain_name):
        print("- Training...")
        for sent in text:
            brain.learn(sent)
    return brain


#cosine is calculated using
#https://stackoverflow.com/questions/15173225/how-to-calculate-cosine-similarity-given-2-sentence-strings-python
def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])

     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     WORD = re.compile(r'\w+')
     words = WORD.findall(text)
     return Counter(words)
"""

def generate_line(prev_line, brain, similarity = 0.8):
    while True:
        new_line =brain.reply(prev_line)
        if get_cosine(text_to_vector(prev_line),text_to_vector(new_line))<similarity:
            return new_line

"""
def generate_line(prev_line, brain, brain_questions, question_prob = 0.2, similarity = 0.3):
    new_line = None
    u = random.random()
    while True:
        if u<question_prob:
            new_line = brain_questions.reply(prev_line)
        else:
            new_line = brain.reply(prev_line)
            
        if new_line and get_cosine(text_to_vector(prev_line),text_to_vector(new_line))>similarity and check_grammar(new_line):
            return new_line

def generate_dialog(brainA, brainA_questions, brainB, brainB_questions, lenght = 10):
    print('Generating a dialog...')
    dialog = []
    lineB = "Hello!"
    while len(dialog)<10:
         lineA = generate_line(lineB, brainA, brainA_questions)
         lineB = generate_line(lineA, brainB, brainB_questions)
         dialog.append(lineA)
         dialog.append(lineB)
    return dialog

def check_grammar(line, max_errors = 2):
    tool = language_check.LanguageTool('en-US')
    matches = tool.check(line)
    if len(matches) > max_errors:
        return False
    else:
        return True


def print_dialog(dialog):
    for line in dialog:
        print(line)

textA_raw = read_file('sheldon.txt')
textB_raw = read_file('dr.house.txt')

textA = clean_text(textA_raw)
textB = clean_text(textB_raw)


questionsA = clean_text(textA_raw, get_questions = True)
questionsB = clean_text(textB_raw, get_questions = True)

bA = learn_text(textA, "cobeA.brain")
bqA = learn_text(questionsA, "cobeA_q.brain")

bB  = learn_text(textB,"cobeB.brain")
bqB = learn_text(questionsB, "cobeB_q.brain")

for i in range(0,5):
    dialog = generate_dialog(bA, bqA, bB, bqB)
    print_dialog(dialog)
    
