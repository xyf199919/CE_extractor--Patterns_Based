import codecs
import csv
import json
import re
import os
import nltk
import operator
import spacy
from nltk.parse import stanford
from nltk.tree import *
from nltk.corpus import wordnet as wn
from tqdm import tqdm

from cmyPackage import *
from cmyPatternMatching import TXT2Patterns, OrderPatterns, MainTokenRegExp

nlp = spacy.load('en_core_web_sm')

Patterns = TXT2Patterns()
Patterns = OrderPatterns(Patterns, True)
mtRegExplst = MainTokenRegExp(Patterns)

with codecs.open('textbook.csv', 'w', 'utf8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Text", "Cause", "Connector", "Effect"])
    with open("tqa/tqa_train_val_test/train/tqa_v1_train.json", "r") as f:
        data = json.loads(f.read())
        for d in tqdm(data):
            topics = d['topics']
            for t in topics:
                text = d['topics'][t]['content']['text']
                sents = [i.text for i in nlp(text).sents]
                group_sents = [' '.join(sents[i:i+3]) for i in range(0, len(sents), 3)]
                for s in group_sents:
                    for p in mtRegExplst:
                        found = p.findall(s)
                        if found:
                            writer.writerows([[s] + list(f) for f in found])
                            break