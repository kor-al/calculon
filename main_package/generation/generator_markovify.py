import re
import math
import random
import os.path
from generation.generator import get_cosine, text_to_vector, GenerativeModel
from generation.cobe_generate import clean_text, read_file
import markovify
import json

#train MC with POS - override classes of markovify
import en_core_web_sm
nlp = en_core_web_sm.load()
class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

class POSifiedNewLineText(markovify.NewlineText):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence

class GenerativeModelMarkovify(GenerativeModel):
    """ Abstract class for a generative model for text """
    def __init__(self, brain_name):
        self._model_name = brain_name
        self.brain_name = './markovify_trained_models/' + brain_name + ".txt"
        self.brain_questions_name = './markovify_trained_models/' + brain_name + "_questions.txt"
        self.brain = None
        self.brain_questions = None
        self.question_prob = 0.3
        self.similarity_min = 0.2

    @property
    def name(self):
        return self._model_name

    def train(self, corpus):
        self.brain_questions = self._learn_corpus(corpus, self.brain_questions_name, questions=True)
        self.brain = self._learn_corpus(corpus, self.brain_name, questions=False)
        return self

    def generate_start(self):
        start_seed = random.choice(['Hello', 'Hi'])
        line = self.brain.make_sentence_with_start(start_seed, strict=False)
        return line

    def generate(self, context):
        u = random.random()
        while True:
            if self.brain_questions and u < self.question_prob:
                new_line = self.brain_questions.make_sentence()
            else:
                new_line = self.brain.make_sentence()

            if not new_line:
                continue

            if new_line and get_cosine(text_to_vector(context, use_stopwords = True), text_to_vector(new_line, use_stopwords = True)) > self.similarity_min:
                return new_line

    def _learn_corpus(self, corpus_file, brain_name, questions=False):
        if not os.path.isfile(brain_name):
            print("- Training...")
            corpus = read_file(corpus_file)
            corpus = clean_text(corpus, get_questions=questions)
            brain = POSifiedText(' '.join(corpus), state_size=3)
            self._save_model(brain, brain_name)
        else:
            brain = self._load_model(brain_name)
        return brain

    def _save_model(self, model, brain_name):
        with open(brain_name, 'w') as outfile:
            json.dump(model.to_json(), outfile)

    def _load_model(self, brain_name):
        return POSifiedText.from_json(json.load(open(brain_name)))

