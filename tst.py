import numpy as np


class TfidfVectorizer():
    def __init__(self):
        self._words = []
        self._dict = {}

    def _create_dict(self, train):
        dictionary = {}
        for doc in train:
            used = set()
            for word in doc.split():
                if word in used:
                    continue
                used.add(word)
                dictionary[word] = dictionary.get(word, 0) + 1

        self._words = sorted(dictionary.items())
        self._dict = {word[0]: idx for idx, word in enumerate(self._words)}

    def fit(self, train):
        self._create_dict(train)
        self._idf = np.log(len(train) / np.array([item[1] for item in self._words]))

    def transform(self, inputs):
        tf = np.zeros((len(inputs), len(self._words)))
        for idx, doc in enumerate(inputs):
            doc_splitted = doc.split()
            for word in doc_splitted:
                if word in self._dict:
                    tf[idx, self._dict[word]] += 1
            tf[idx] /= len(doc_splitted)
        return tf * self._idf


train = [
    'a a a',
    'a b',
    'c',
]
test = [
    'a c',
    'd',
]

tf_idf_vect = TfidfVectorizer()
tf_idf_vect.fit(train)

print(tf_idf_vect._words)
print(tf_idf_vect._dict)
print(tf_idf_vect._idf)

print(tf_idf_vect.transform(test))
