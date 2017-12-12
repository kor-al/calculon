import sys
import random
from operator import itemgetter
from evaluation.evaluation import DialogEvaluator
from generation.generator import GenerativeModel
from tqdm import tqdm
#from generation.generator_markovify import GenerativeModelMarkovify

class Calculon:
    def __init__(self):
        print("- Initiating Calculon")
        self._models = {}
        print("- Initiating DialogEvaluator")
        self._evaluator = DialogEvaluator()

    def add_model(self, model):
        print("- Adding model %s" % model.name)
        self._models[model.name] = model

    @property
    def characters(self):
        return list(self._models.keys())

    def _get_response(self, dialog, model, context_length, tries, n, debug):
        generated = []
        # Generate several responses to be evaluated
        for _ in tqdm(range(tries), ncols=50):
            previous_sentences = dialog[-context_length:]
            response = model.generate(dialog[-1])

            # sentence evaluation
            accepted, score = self._evaluator.evaluate(previous_sentences, response)
            while not accepted: # keep going until a good response is found
                response = model.generate(dialog[-1])
                accepted, score = self._evaluator.evaluate(previous_sentences, response)
            generated.append((response, score)) # save the response and its score
            if debug:
                print("\t- Candidate: %s  ->  %f" % (response, score))

        # Sort the generated responses based on their score
        end = int(max(1, len(generated)*n))
        generated = sorted(generated, key=itemgetter(1), reverse=True)
        generated = generated[:end]
        return random.choice(generated)[0]

    def chat(self, character, context_length=4, tries=10, n=0.4, debug=False):
        dialog = []
        while True:
            try:
                sentence = input("Me: ")
                dialog.append(sentence)
                response = self._get_response(dialog, self._models[character],
                        context_length, tries, n, debug)
                print(character + ": " + response)

            except KeyboardInterrupt:
                return

    def generate(self, name1, name2, length=10, context_length=4, tries=20, n=0.4, debug=False):
        if debug:
            print("- Generating dialog")

        characters = [self._models[name1], self._models[name2]]
        current = 0
        dialog = [characters[current].generate_start()]
        current = 1

        while len(dialog) < length:
            print("(Dialog length %d/%d)" % (len(dialog), length))
            response = self._get_response(dialog, characters[current],
                    context_length, tries, n, debug)
            dialog.append(response)

            if debug:
                print(characters[current].name + ": " + response)

            current = (current + 1) % 2 # change character

        return '\n'.join(dialog)


def main():
    SHELDON = './data_scraping_subpackage/sheldon.txt'
    HOUSE = './data_scraping_subpackage/dr.house.txt'

    calculon = Calculon()
    calculon.add_model(GenerativeModel("sheldon").train(SHELDON))
    calculon.add_model(GenerativeModel("house").train(HOUSE))

    #calculon.add_model(GenerativeModelMarkovify("sheldon").train(SHELDON))
    #calculon.add_model(GenerativeModelMarkovify("house").train(HOUSE))

    # COMMAND LINE INTERFACE
    if len(sys.argv) > 1:
        if len(sys.argv) > 2 and sys.argv[1] == "chat":
            for character in calculon.characters:
                if sys.argv[2] == character:
                    calculon.chat(character)

        elif sys.argv[1] == "generate":
            print(calculon.generate(calculon.characters[0], calculon.characters[1]))

if __name__ == '__main__':
    main()

