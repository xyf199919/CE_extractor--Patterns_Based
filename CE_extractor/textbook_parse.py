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

from cmyPatternMatching import TXT2Patterns, OrderPatterns, MainTokenRegExp, GettingCEcases

# --------- people hypernym set ------------------
PEOPLE = ('person', 'individual', 'someone', 'somebody', 'mortal', 'soul', 'being', 'human', 'hominid', 'humans', 'man',
          'mankind')
### ---- stanford_parser java package ----  
os.environ['STANFORD_PARSER'] = r'../../stanford-parser.jar'
os.environ['STANFORD_MODELS'] = r'../../stanford-parser-3.5.2-models.jar'
### ---- JAVA_HOME path ----
java_path = r"C:\Program Files\Java\jdk1.8.0_45\bin\java.exe"
os.environ['JAVAHOME'] = java_path
### ---- initiate a parser ---- 
parser = stanford.StanfordParser(model_path=r"../../englishPCFG.ser.gz")

def ptree(sent):
    return parser.raw_parse(sent)

nlp = spacy.load('en_core_web_sm')

Patterns = TXT2Patterns()
Patterns = OrderPatterns(Patterns, True)
mtRegExplst = MainTokenRegExp(Patterns)
emptyTree = Tree('ROOT', [])

with codecs.open('textbook.csv', 'w', 'utf8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["PatternID", "Text", "Cause", "Effect"])
    with open("tqa/tqa_train_val_test/train/tqa_v1_train.json", "r") as f:
        data = json.loads(f.read())
        for d in tqdm(data):
            topics = d['topics']
            for t in topics:
                text = d['topics'][t]['content']['text']
                textbook_sentences = [i.text for i in nlp(text).sents]
                tlen = len(textbook_sentences)
                for ti in range(len(textbook_sentences)):
                    prev_sent = "" if ti < 1 else textbook_sentences[ti - 1]
                    next_sent = "" if ti > tlen - 2 else textbook_sentences[ti + 1]
                    sent = textbook_sentences[ti]
                    pppt = ptree(sent)
                    if pppt == []:
                        continue
                    curPT = pppt[0]
                    prePT = emptyTree if ti < 1 or ptree(textbook_sentences[ti - 1]) == [] else ptree(textbook_sentences[ti - 1])[0]
                    nextPT = emptyTree if ti > tlen - 2 or ptree(textbook_sentences[ti + 1]) == [] else ptree(textbook_sentences[ti + 1])[0]
                    sentCEset = GettingCEcases(Patterns, mtRegExplst, prePT, curPT, nextPT)
                    if sentCEset == []:
                        continue
                    for ce in sentCEset:
                        try:
                            writer.writerow([
                                ce.pt.id,
                                prev_sent + " " + sent + " " + next_sent,
                                u' '.join(ce.cause.PTree.leaves()),
                                u' '.join(ce.effect.PTree.leaves())
                            ])
                        except:
                            print(sent)
