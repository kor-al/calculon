#markov chains
import markovify
import re
import nltk
import string
from nltk.tokenize.moses import MosesDetokenizer, MosesTokenizer
from gensim.summarization import keywords
import RAKE #https://github.com/fabianvf/python-rake

#train MC with POS - override classes of markovify
import en_core_web_sm
nlp = en_core_web_sm.load()
class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

def sanitize(token_list):
    """
    Sanitize tokens:
    - Words consisting only of letters and '-' are considered as 'words'.
    - Numbers and words with apostrophes are also good
    - Save all the punctuation
    :param token_list: original list of tokens
    :return: sanitized list of tokens
    """

    is_word = re.compile(r'(^[a-zA-Z]*$)|(^[0-9]+$)|(^(?=.*\w)^(\w|\')+$)|(^(&apos;)(\w)+$)|(^\w+(?:-\w+)+$)')
    #words, numbers, words with an apostrophes and dashes
    return [token for token in token_list if is_word.match(token) or token in string.punctuation]# + ['.']

def clean_text(raw_text, newline = False):
    """
    Words consist of letters or numbers
    :param raw_text: text (not divided into sentences)
    :return: list of sanitized sentences
    """
    # Tokenize text into sentences.
    sentences = nltk.sent_tokenize(raw_text)

    #Tokenize each sentence
    sanitized_sentences = []
    for s in sentences:
        #use Moses instead of nltk.word_tokenize(s)  - better with apostrophes: cant -> (can + 't) but not (ca + 'n't)
        tokenizer = MosesTokenizer()
        s_tokens = tokenizer.tokenize(s)
        #s_tokens = nltk.word_tokenize(s)
        sanitized_sentences.append(sanitize(s_tokens))

    #Sanitized tokens joined using detokenizer
    detokenizer = MosesDetokenizer()
    if newline:
        return [detokenizer.detokenize(s, return_str=True)+'\n' for s in sanitized_sentences]
    return [detokenizer.detokenize(s, return_str=True) for s in sanitized_sentences]
    #return ["".join([" "+i if not i.startswith("'") and i not in ['\'','n\'t'] else i for i in s]).strip() for s in sanitized_sentences]

def generate_mc(model, seed = None, pos = "start", model_rev = None):
    """
    Generate a sentence using Markov Chain models
    :param model: MC model (direct)
    :param seed: seed to start sentence
    :param pos: position of the seed: "start", "middle", "end"
    :param model_rev: MC model (reversed) to generate sentences with a seed in the middle/end
    :return: a sentence
    """
    res,res1 = None, None
    if not seed:
        while not res:
            res = model.make_sentence()
    else:
        if pos=='start': #place seed in the beginning
            while not res:
                res = model.make_sentence_with_start(seed, strict=False)
        elif pos == 'middle':
            while not res and not res1:
                res = model.make_sentence_with_start(seed, strict=True)
                res1 = model_rev.make_sentence_with_start(seed, strict=True)
                return " ".join(res1.split(" ")[::-1][:-1]) + ' ' + res
        elif pos == 'end':
            while not res:
                res = model_rev.make_sentence_with_start(seed, strict=False)
            res = " ".join(res.split(" ")[::-1])
        else:
            raise ValueError('Invalid starting position')

    return res

def extract_keywords(text, method = "gensim", ratio = 0.5):
    while True:
        if method == "gensim":
            try:
                return keywords(text, ratio=ratio,pos_filter=['NN', 'VB', 'JJ'], split = True)
            except:
                method = 'nouns'
        elif method == "rake":
            Rake = RAKE.Rake(RAKE.SmartStopList()+["don",'ll'])
            try:
                return [w for (w,c) in Rake.run(text, minCharacters=1, maxWords=1, minFrequency=1)]
            except:
                method = 'nouns'
        elif method == "nouns":
            print('>Nouns method')
            nouns = []
            for word in nlp(text):
                if word.pos_ == 'NOUN':
                    nouns.append(word.orth_)
            return nouns




################
file = 'temp.txt'
file_raw = None

with open(file, 'r', encoding='utf8') as f:
    file_raw = f.read()

# And replace more than one subsequent whitespace chars with one space
text = re.sub(r'\s+', ' ', file_raw)

text_reversed = " ".join(text.split(" ")[::-1])

#use text model of markovify
text = clean_text(text)
text_reversed = clean_text(text_reversed)

text_model = markovify.Text(text, state_size=1)
text_model_rev = markovify.Text(text_reversed, state_size=1)
res = generate_mc(text_model, seed = "I", pos = "start", model_rev = text_model_rev)
print(res)

#use NewLine model of markovify
#text = clean_text(text,True)
#print(text)
#text_reversed = clean_text(text_reversed,True)

#text_model = markovify.NewlineText(' '.join(text), state_size=1)
#text_model_rev = markovify.NewlineText(' '.join(text_reversed), state_size=1)
#res = generate_mc(text_model, seed = "I", pos = "start", model_rev = text_model_rev)
#print(res)

print("Keywords with Gensim method (if it fails, all nouns are extracted):")
kws = extract_keywords(res, method = "gensim", ratio = 0.5)
print(kws)
print("Keywords with Rake method:")
kws = extract_keywords(res, method = "rake")
print(kws)


# Print five randomly-generated sentences
#for i in range(5):
#    print(text_model.make_sentence())

#for i in range(3):
#    print(text_model.make_short_sentence(140))
