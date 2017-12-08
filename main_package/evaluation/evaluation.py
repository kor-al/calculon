from collections import Counter
from string import punctuation
from nltk.corpus import stopwords
import numpy as np
import gensim

class DialogEvaluator:
    def __init__(self, word_model='google-w2v.bin'):
        """ Load Google's slim word2vec model """
        self._word_model = gensim.models.KeyedVectors.load_word2vec_format(word_model, binary=True)
        self._word_vectors = self._word_model.wv

    def _likelihood(self, sentence):
        """ Return score between 0 and 10, indicating the sentence likelihood 
            TODO: use Bayes Classifier
        """

        #return self._word_model.score([sentence.split()])*10
        return 0 # yet to implement

    def _weighted_sum(self, sentence, counts):
        vectors = []
        for word in sentence.split():
            if word in stopwords.words('english') + list(punctuation):
                continue
            vec = np.copy(self._word_vectors[word])
            if word in counts:
                vec *= counts[word]

            vectors.append(vec)

        return np.sum(vectors)

    def correlation(self, sentence1, sentence2, dialog):
        """ Evaluate the relationship between two sentences
            using averaged Word2Vec vectors and tf-idf values as weights
            TODO: use bigrams
                  use tf-idf trained on opposite character's dialog

            INPUT:
            sentence1, sentence2     -   sentences to be evaluated
            dialog (list of strings) -   dialog generated so far (used as a context)

            OUTPUT:
            score between 0 and 10 where 0 is min and 10 is maximum correlation
        """

        counts = None
        if dialog:
            #TODO: REMOVE PUNCTUATION
            counts = Counter('\n'.join(dialog + [sentence1, sentence2]).split())

        score = np.linalg.norm(
                self._weighted_sum(sentence1, counts) - 
                self._weighted_sum(sentence2, counts)
                )

        score = min(score, 10)
        return 10 - score

    def evaluate(self, sentence1, sentence2, dialog=None):
        score = self.correlation(sentence1, sentence2, dialog)
        score += self._likelihood(sentence1)
        score += self._likelihood(sentence2)
        return score


########### JUST A TEST ############
def main():
    ev = DialogEvaluator()
    dialog = ['table cat', 'hey how is it going?', 'fine thanks']
    print(ev.evaluate('the cat is on the table', 'the cat is under the desk', dialog))

if __name__ == '__main__':
    main()

