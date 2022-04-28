import glob
import re

import nltk
import json
import re
import gensim
from gensim.models.keyedvectors import KeyedVectors
import math
import numpy as np
from nltk.corpus import stopwords


nltk.download('stopwords')
stop_words = stopwords.words('english')


folder_name = ["CS61A", "CS61B", "DS100"]

model = KeyedVectors.load_word2vec_format("wiki-news-300d-1M-subword.vec", binary=False)
    
def get_documents(path):
    file_sentences = {}
    for folder in folder_name:
        files = glob.glob(os.path.join(path, folder, "*"))
        sentences = []
        for file in files:
            with open(file, "r") as f:
                content_jsons = json.load(f)
                for content_json in content_jsons:
                    text = "".join([content["text"] for content in content_json["contents"]])
                    sentences.extend(re.split("[.?]", text))
            file_sentences[folder] = sentences
            
    return file_sentences

def phrase_2_vec(phrase):
    phrase = phrase.lower()
    wordsInPhrase = [word for word in phrase.split() if word not in stop_words]
    
    vectorSet = []
    for aWord in wordsInPhrase:
        try:
            wordVector=model[aWord]
            vectorSet.append(wordVector)
        except:
            pass
    return np.mean(vectorSet, axis = 0)


def cosine_similarity(vec1, vec2):
    cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    try:
        if math.isnan(cosine_similarity):
            cosine_similarity=0
    except:
        cosine_similarity=0
    return cosine_similarity


def get_sent_vector(sent1, sent2):
    return cosine_similarity(phrase_2_vec(sent1), phrase_2_vec(sent2))

def get_answerability(file_sentences, post):
    title = post["title"]
    course = post["course"]
    is_answerable = post["is_answerable"]
    
    if is_answerable == "True":
        sentences = file_sentences.get(course, None)
        if sentences is not None:
            similarity = [(i, get_sent_vector(sent, title)) for i, sent in enumerate(sentences)]
            similarity.sort(key=lambda x:x[1], reverse=True)
            return similarity[0][1] > 0.82

    return is_answerable


file_sentences = get_documents("./.cache/documents/")


with open("parrot-qa-answerability.json", "r") as f:
    qa_json = json.load(f)
    for qa_pair in qa_json["qa_pairs"]:
        qa_pair["is_answerable"] = bool(get_answerability(file_sentences, qa_pair))

with open("parrot-qa-answerability-filtered.json", "r") as f:
    f.write(json.dumps(qa_json))