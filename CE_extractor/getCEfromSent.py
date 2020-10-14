#######################################################################################
# ---------------------------------- Global variable -------------------------------- #
#######################################################################################
import os
import nltk
import re
import operator
import csv
import codecs
from cmyPackage import *
from nltk.parse import stanford
from nltk.tree import *
from nltk.corpus import wordnet as wn

# --------- set some folder path ------------------
corpdir = os.path.join(os.getcwd(), "Corpus")
pkdir = os.path.join(os.getcwd(), "PK")
TXTcorpdir = os.path.join(os.getcwd(), "Corpus", "TXT")
TXTpkdir = os.path.join(os.getcwd(), "PK", "TXT")
DICpkdir = os.path.join(os.getcwd(), "PK", "DIC")
ctxtdir = os.path.join(os.getcwd(), "CheckTXT")
xlsdir = os.path.join(os.getcwd(), 'XLS')
dbfile = os.path.join(os.getcwd(), 'CErelation.accdb')
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

from cmyPatternMatching import *


def check():
    textbook_sentences = ["He never lies; therefore, everyone likes to make friends with him.", "Japan will be on the dark side of the Earth , and thus will lack the warming influence of the Sun ."]
    textbook_sentences.append("this is a test, so it should pass.")
    textbook_sentences.append("this should pass because it's a test!")
    ### ---- get Patterns and mtRegExplst ----
    Patterns = TXT2Patterns()
    Patterns = OrderPatterns(Patterns, True)
    mtRegExpList = MainTokenRegExp(Patterns)

    emptyTree = Tree('ROOT', [])
    plen = len(Patterns)

    TestRecfp = os.path.join(ctxtdir, 'PatternsTestRecoding.txt')
    # pt_txt_fp = os.path.join(ctxtdir, 'patterns2.txt')
    TestRec = codecs.open(TestRecfp, 'w', 'utf8')
    # pt_txt = codecs.open(pt_txt_fp, 'w', 'utf8')

    for ti in range(len(textbook_sentences)):
        sent = textbook_sentences[ti]
        # pt_txt.write('ID:%d' % pt.id + '  Freq:%d' % pt.pfreq + ' %s' % pt.main_token + "----" + ' %s' % pt.constraints + '\n')
        print "*****************************************************"
        print "Processing sentence ", ti
        print "input", sent

        pppt = parser.raw_parse(sent)[0]
        # print pppt
        # PTset = []
        # for str in pt.cases:
        #     PTset.extend(parser.raw_parse(str))

        # for pppt in PTset:
        CEcases = GettingCEcases(Patterns, mtRegExpList, emptyTree, pppt, emptyTree)
        if CEcases == []:
            print "sent : ", ' '.join(pppt.leaves()), "cannot match!\n"
        else:
            for ce in CEcases:
                TestRec.write("Sent: " + ' '.join(pppt.leaves()) + '\n')
                TestRec.write(
                    "pattern: " + '%d' % ce.pt.id + ' %s' % ce.pt.main_token + "----" + ' %s' % ce.pt.constraints + '\n')
                TestRec.write(
                    "Cause: " + ' '.join(ce.cause.PTree.leaves()) + '\n')  # " -- "+ str(ce.cause.span)+'\n');
                TestRec.write(
                    "Effect: " + ' '.join(ce.effect.PTree.leaves()) + '\n')  # " -- "+ str(ce.effect.span)+'\n');
                TestRec.write("\n")
    TestRec.close()
    # pt_txt.close()

def get_ce_from_sentences(textbook_sentences, output_filename):
    # example input:
    # textbook_sentences = ["He never lies; therefore, everyone likes to make friends with him.", "Japan will be on the dark side of the Earth , and thus will lack the warming influence of the Sun ."]
    # textbook_sentences.append("this is a test, so it should pass.")
    # textbook_sentences.append("this should pass because it's a test!")
    # textbook_sentences.append("this is a cause.")
    # textbook_sentences.append("Therefore, this is the result.")
    # textbook_sentences.append("A commission spokesman said the incidents appeared to amount to discrimination on religious grounds.")

    tlen = len(textbook_sentences)
    ### ---- get Patterns and mtRegExplst ----
    Patterns = TXT2Patterns()
    Patterns = OrderPatterns(Patterns, True)
    mtRegExpList = MainTokenRegExp(Patterns)

    emptyTree = Tree('ROOT', [])
    plen = len(Patterns)

    csvfile = codecs.open(output_filename, 'w', 'utf8')
    writer = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(["Pattern_id", "Text", "Cause", "Effect"])
    # TestRecfp = os.path.join(ctxtdir, 'PatternsTestRecoding.txt')
    # TestRec = codecs.open(TestRecfp, 'w', 'utf8')

    for ti in range(len(textbook_sentences)):
        sent = textbook_sentences[ti]
        if ptree(sent) == []:
            continue
        print "*****************************************************"
        print "Processing sentence ", ti
        # print "input", sent

        curPT = ptree(sent)[0]
        prePT = emptyTree if ti < 1 or ptree(textbook_sentences[ti - 1]) == [] else ptree(textbook_sentences[ti - 1])[0]
        nextPT = emptyTree if ti > tlen - 2 or ptree(textbook_sentences[ti + 1]) == [] else ptree(textbook_sentences[ti + 1])[0]

        sentCEset = GettingCEcases(Patterns, mtRegExpList, prePT, curPT, nextPT)
        if sentCEset == []:
            print "middle sent : ", ' '.join(curPT.leaves()), "cannot match!\n"
        else:
            for ce in sentCEset:
                #writer.writerow(["Pattern_id", "Text", "Cause", "Effect"])
                row = []
                row.append(ce.pt.id)
                prev_middle_next = ' '.join(prePT.leaves()) + ' '.join(curPT.leaves()) + ' '.join(nextPT.leaves())
                row.append(prev_middle_next)
                cause = ' '.join(ce.cause.PTree.leaves())
                effect = ' '.join(ce.effect.PTree.leaves())
                row.append(cause)
                row.append(effect)

                writer.writerow(row)
                # TestRec.write("prev Sent: " + ' '.join(prePT.leaves()) + '\n')
                # TestRec.write("Middle Sent: " + ' '.join(curPT.leaves()) + '\n')
                # TestRec.write("next Sent: " + ' '.join(nextPT.leaves()) + '\n')
                # TestRec.write(
                #     "pattern: " + '%d' % ce.pt.id + ' %s' % ce.pt.main_token + "----" + ' %s' % ce.pt.constraints + '\n')
                # TestRec.write(
                #     "Cause: " + ' '.join(ce.cause.PTree.leaves()) + '\n')  # " -- "+ str(ce.cause.span)+'\n');
                # TestRec.write(
                #     "Effect: " + ' '.join(ce.effect.PTree.leaves()) + '\n')  # " -- "+ str(ce.effect.span)+'\n');
                # TestRec.write("\n")
    # TestRec.close()

def ptree(sent):
    return parser.raw_parse(sent)

if __name__ == "__main__":
    # check()
    # textbook_sentences = ["He never lies; therefore, everyone likes to make friends with him.", "Japan will be on the dark side of the Earth , and thus will lack the warming influence of the Sun ."]
    # textbook_sentences.append("this is a test, so it should pass.")
    # textbook_sentences.append("this should pass because it's a test!")
    # textbook_sentences.append("this is a cause.")
    # textbook_sentences.append("Therefore, this is the result.")
    # textbook_sentences.append("A commission spokesman said the incidents appeared to amount to discrimination on religious grounds.")
    # get_ce_from_sentences(textbook_sentences, "emily_test_output_demo.csv")
