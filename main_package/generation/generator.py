from cobe.brain import Brain
import math
import random
from collections import Counter
import os.path


class GenerativeModel(object):
    """ Abstract class for a generative model for text """
    
    def __init__(self, brain_name):
        self.brain_name = brain_name + ".brain"
        self.brain_questions_name = brain_name + "_questions.brain"
        self.brain = None
        self.brain_questions = None
        self.question_prob = 0.3
        self.similarity_min = 0.6

    def train(self, corpus, corpus_questions = None):
        self.brain = self._learn_corpus(corpus, self.brain_name)
        if corpus_questions:
            self.brain_questions = self._learn_corpus(corpus_questions, self.brain_questions_name)
        return self

    def generate_start(self):
        start_seed = random.choice(['Hello', 'Hi'])
        line = self.generate(start_seed)
        return line

    def generate(self, context):
        u = random.random()
        while True:
            if brain_questions and u < self.question_prob:
                new_line = self.brain_questions.reply(context)
            else:
                new_line = self.brain.reply(context)

            if new_line and get_cosine(text_to_vector(context), text_to_vector(new_line)) > self.similarity_min:
                return new_line

    def _learn_corpus(self,text,brain_name):
        brain = Brain(brain_name)
        if not os.path.isfile(brain_name):
            print("- Training...")
            for sent in text:
                brain.learn(sent)
        return brain

    # cosine is calculated using
    # https://stackoverflow.com/questions/15173225/how-to-calculate-cosine-similarity-given-2-sentence-strings-python
def get_cosine(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def text_to_vector(text):
    WORD = re.compile(r'\w+')
    words = WORD.findall(text)
    return Counter(words)
