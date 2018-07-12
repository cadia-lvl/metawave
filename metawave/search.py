import os


class SearchHandler:
    def __init__(self, token_dir):
        self._token_dir = token_dir

    def search(self, term):
        results = []

        for filename in os.listdir(self._token_dir):
                with open(os.path.join(self._token_dir,filename), 'r') as f:
                    tok = ''.join(line.strip() for line in f)
                    if term in tok:
                        results.append({'id':filename, 'tok': tok})
        return results
