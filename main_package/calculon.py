from operator import itemgetter
from evaluation.evaluation import DialogEvaluator
from generation.generator import GenerativeModel
from generation.cobe_generate import read_file, clean_text

class Calculon:
    def __init__(self):
        print("- Initiating Calculon")
        self._models = {}
        print("- Initiating DialogEvaluator")
        self._evaluator = DialogEvaluator()

    def add_model(self, model):
        print("- Adding model %s" % model.name)
        self._models[model.name] = model

    def generate(self, name1, name2, length=10, context_length=4, tries=20):
        print("- Generating dialog")
        characters = [self._models[name1], self._models[name2]]
        current = 0
        dialog = [characters[current].generate_start()]
        current = (current + 1) % 2

        while len(dialog) < length:
            print("(Dialog length %d)" % len(dialog))
            generated = []
            # Generate several responses to be evaluated
            for _ in range(tries):
                previous_sentences = dialog[-context_length:]
                response = characters[current].generate(dialog[-1])

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


def main():
    SHELDON = './data_scraping_subpackage/sheldon.txt'
    HOUSE = './data_scraping_subpackage/house.txt'

    calculon = Calculon()
    calculon.add_model(GenerativeModel("sheldon").train(SHELDON))
    calculon.add_model(GenerativeModel("house").train(HOUSE))

    dialog = calculon.generate("sheldon", "house", length=10, tries=20)
    print(dialog)


if __name__ == '__main__':
    main()








