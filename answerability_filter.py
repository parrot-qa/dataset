import os
import re
import json
import math

from common import DATA_DIR

import nltk
import gensim
from gensim.models.keyedvectors import KeyedVectors
import numpy as np
from nltk.corpus import stopwords


nltk.download('stopwords')
stop_words = stopwords.words('english')


model = KeyedVectors.load_word2vec_format(
    # Download here: https://fasttext.cc/docs/en/english-vectors.html
    os.path.join(DATA_DIR, "wiki-news-300d-1M-subword.vec"),
    binary=False
)


def get_documents(documents):
    file_sentences = {}
    for doc in documents:
        course = doc["course"]
        if course not in file_sentences:
            file_sentences[course] = []
        text = doc["passage_text"]
        file_sentences[course].extend(re.split("[.?]", text))

    return file_sentences


def phrase_2_vec(phrase):
    phrase = phrase.lower()
    wordsInPhrase = [word for word in phrase.split() if word not in stop_words]

    vectorSet = []
    for aWord in wordsInPhrase:
        try:
            wordVector = model[aWord]
            vectorSet.append(wordVector)
        except:
            pass
    return np.mean(vectorSet, axis=0)


def cosine_similarity(vec1, vec2):
    cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    try:
        if math.isnan(cosine_similarity):
            cosine_similarity = 0
    except:
        cosine_similarity = 0
    return cosine_similarity


def get_sent_vector(sent1, sent2):
    return cosine_similarity(phrase_2_vec(sent1), phrase_2_vec(sent2))


def get_answerability(file_sentences, post):
    title = post["title"]
    course = post["course"]
    is_answerable = post["is_answerable"]

    if is_answerable == True:
        sentences = file_sentences.get(course, None)
        if sentences is not None:
            similarity = [(i, get_sent_vector(sent, title)) for i, sent in enumerate(sentences)]
            max_similarity = max(similarity, key=lambda x: x[1])[1]
            return max_similarity > 0.82

    return is_answerable


with open(os.path.join(DATA_DIR, "parrot-qa.json"), "r") as f:
    qa_json = json.load(f)

file_sentences = get_documents(qa_json['documents'])
for qa_pair in qa_json["qa_pairs"]:
    qa_pair["is_answerable"] = bool(get_answerability(file_sentences, qa_pair))

with open(os.path.join(DATA_DIR, "parrot-qa-filtered.json"), "w") as f:
    json.dump(qa_json, f, indent=4)
