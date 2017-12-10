class GenerativeModel(object):
    """ Abstract class for a generative model for text """
    def train(self, corpus):
        raise NotImplementedError('Not implemented')
        return self

    def generate_start(self):
        raise NotImplementedError('Not implemented')

    def generate(self, context):
        raise NotImplementedError('Not implemented')

