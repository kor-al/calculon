from string import punctuation
from collections import Counter, defaultdict
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from nltk.translate.gleu_score import sentence_gleu
import language_check
import numpy as np
import gensim

class DialogEvaluator:
    def __init__(self, word_model='./evaluation/google-w2v.bin'):
        """ Load Google's slim word2vec model """
        print("- Loading Google's Word2Vec model")
        self._word_model = gensim.models.KeyedVectors.load_word2vec_format(word_model, binary=True)
        self._word_vectors = self._word_model.wv

    def _likelihood(self, sentence):
        """ Return score between 0 and 1, indicating the sentence likelihood 
            TODO: use Bayes Classifier
        """

        #return self._word_model.score([sentence.split()])*10
        return 1 # yet to implement

    def _tf_weighted_sum(self, sentence, counts):
        """ Calculate the sum of the words of a given sentence translated into
            a vector space using a pre-trained Word2Vec model.
            Each word-vector is weighted by its influence in the text, estimated
            by the counter collection passed as input.

            INPUT:
            sentence    -   sentence to be traslated into a list of vectors
            counts      -   Counter collection wich may include the term
                            frequency (tf) for the given sentence along with
                            the tf from the whole dialog
            OUTPUT:
            max([c_0, ..., c_n]*[w_0, ..., w_n], 10)/10

        """
        vectors = []
        for word in word_tokenize(sentence):
            if word in stopwords.words('english') + list(punctuation):
                continue
            vec = np.copy(self._word_vectors[word])
            if word in counts:
                vec *= counts[word]

            vectors.append(vec)

        return max(np.sum(vectors), 10)/10

    def grammar_score(sentence):
        """ Evaluate the grammatical correctness of a given sentence.
            INPUT: sentence     -   sentence to be evaluated

            OUTPUT: score       -   from 0 to 1, where 1 is grammatically correct
                    corrected   -   corrected sentence
        """
        tool = language_check.LanguageTool('en-US')
        errors = tool.check(sentence)
        default_score = 0.5

        #TODO: weight other error types
        errors_score = {   
                'I_LOWERCASE' : 0.1,
                'UPPERCASE_SENTENCE_START' : 0.05
                }
        errors_score = defaultdict(lambda: default_score, errors_score)

        score = 1
        for error in errors:
            score -= errors_score[error.ruleId]

        return max(0, score), language_check.correct(sentence, errors)

    def correlation(self, prev_sentences, response, dialog):
        """ Evaluate the relationship between every pair of sentences
            <previous_i, response> for i in [0, len(prev_sentence)]
            using averaged Word2Vec vectors and term-frequencies as weights.
            Also compute translation metrics scores using the previous lines as
            given references and the response as the translation hypothesis.

            TODO: - use bigrams
                  - use tf-idf trained on opposite character's dialog
                  - add more metrics (ROUGE, NIST, LEPOR, ...)

            INPUT:
            prev_sentences  -   list of previous sentences in the dialog
            response        -   response to the last sentence
            dialog          -   dialog generated so far (used as context)

            OUTPUT:
            score between 0 and MAX, where MAX is the maximum correlation score.
            MAX is just the number of metrics used to evaluate the correlation;
            it has yet to be established.
        """
        #0) Compute term frequency for each word from the given corpus
        score = 0.0
        counts = None
        corpus = prev_sentences + [response]

        if dialog:
            corpus += dialog

        counts = Counter(word_tokenize('\n'.join(corpus)))

        #1) Calculate weighted vector distance between every pair <previous_i, response>
        #   and compute the mean of such distances
        vect_dist = 0.0
        for previous in prev_sentences:
            vect_dist += 1 - np.linalg.norm(
                    self._tf_weighted_sum(previous, counts) - 
                    self._tf_weighted_sum(response, counts))
        
        #TODO: scale down the weight as going back into the dialog history
        score += vect_dist/len(prev_sentences)

        #2) Sentence-level translation metrics (BLEU, GLEU)
        f = SmoothingFunction().method3
        bleu = sentence_bleu(prev_sentences, response, smoothing_function=f)
        gleu = sentence_gleu(prev_sentences, response)
        metrics_score = np.mean([bleu, gleu])

        score += metrics_score

        return score

    def evaluate(self, previous, response, dialog=None):
        score = self.correlation(previous, response, dialog)
        score += self._likelihood(response)
        score += DialogEvaluator.grammar_score(response)[0]
        return score > 4*0.6, score

########### JUST A TEST ############
def main():
    ev = DialogEvaluator()
    previous = [
            'the cat was on the table',
            'no, i think the cat is still on it',
            'you are right, it is still on the table'
            ]
    response = 'of course i am right, the cat is on the table!'

    print(ev.evaluate(previous, response))

if __name__ == '__main__':
    main()

