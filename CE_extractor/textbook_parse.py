import codecs
import csv
import json
import re
import os
import nltk
import operator

from nltk.parse import stanford
from nltk.tree import *
from nltk.corpus import wordnet as wn
from tqdm import tqdm

from cmyPackage import *
from cmyPatternMatching import TXT2Patterns, OrderPatterns, MainTokenRegExp

Patterns = TXT2Patterns()
Patterns = OrderPatterns(Patterns, True)
mtRegExplst = MainTokenRegExp(Patterns)

with codecs.open('textbook.csv', 'w', 'utf8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
    with open("tqa/tqa_train_val_test/train/tqa_v1_train.json", "r") as f:
        data = json.loads(f.read())
        for d in tqdm(data):
            topics = d['topics']
            for t in topics:
                text = d['topics'][t]['content']['text']
                for p in mtRegExplst:
                    found = p.findall(text)
                    if found:
                        writer.writerows(found)
                        break
