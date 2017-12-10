from operator import itemgetter
from evaluation.evaluation import DialogEvaluator
#from generation.generator import GenerativeModel

class Calculon:
    def __init__(self):
        self._models = {}
        self._evaluator = DialogEvaluator()

    def add_model(self, name, model):
        self._models[name] = model.train()

    def generate(self, name1, name2, length=10, context_length=4, tries=20):
        characters = [self._models[name1], self._models[name2]]
        current = 0
        dialog = [characters[current].generate_start()]
        current = (current + 1) % 2

        while len(dialog) < length:
            generated = []
            # Generate several responses to be evaluated
            for _ in range(tries):
                previous_sentences = dialog[-context_length:]
                response = characters[current].generate(dialog)

                # sentence evaluation
                accepted, score = self._evaluator.evaluate(previous_sentences, response)
                while not accepted: # keep going until a good response is found
                    accepted, score = self._evaluator.evaluate(previous_sentences, response)
                generated.append((response, score)) # save the response and its score

            # Sort the generated responses based on their score
            generated = sorted(generated, key=itemgetter(1))
            dialog.append(generated[-1][0])
            current = (current + 1) % 2

        return '\n'.join(dialog)







