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

f = open("errors.txt", "w", encoding="utf-8")
mem_errors, encoding_errors = 0, 0

def ptree(sent):
    global mem_errors
    try:
        return parser.raw_parse(sent)
    except:
        mem_errors += 1
        f.write("M: ")
        f.write(sent)
        f.write("\n")
        return [emptyTree]

nlp = spacy.load('en_core_web_sm')

Patterns = TXT2Patterns()
Patterns = OrderPatterns(Patterns, True)
mtRegExplst = MainTokenRegExp(Patterns)
emptyTree = Tree('ROOT', [])

with codecs.open('squad_ce.csv', 'w', 'utf8') as csvfile:
    writer = csv.writer(csvfile, delimiter=',',
                                quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["PatternID", "Text", "Cause", "Effect"])
    with open("dev-v2.0.json", "r") as f:
        data = json.load(f)['data']
        total = sum([len(article["paragraphs"]) for article in data])
        with tqdm(total=total) as pbar:
            for article in data:
                paras = article["paragraphs"]
                for para in paras:
                    text = para["context"]
                    sentences = [i.text for i in nlp(text).sents]
                    tlen = len(sentences)
                    for ti in tqdm(range(len(sentences))):
                        prev_sent = "" if ti < 1 else sentences[ti - 1]
                        next_sent = "" if ti > tlen - 2 else sentences[ti + 1]
                        sent = sentences[ti]
                        pppt = ptree(sent)
                        if pppt == []:
                            continue
                        curPT = pppt[0]
                        prePT = emptyTree if ti < 1 or ptree(sentences[ti - 1]) == [] else ptree(sentences[ti - 1])[0]
                        nextPT = emptyTree if ti > tlen - 2 or ptree(sentences[ti + 1]) == [] else ptree(sentences[ti + 1])[0]
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
                                encoding_errors += 1
                                f.write("E: ")
                                f.write(sent)
                                f.write("\n")
                    pbar.update(1)

print(mem_errors, encoding_errors)
f.write("{}, {}".format(mem_errors, encoding_errors))
f.close()
