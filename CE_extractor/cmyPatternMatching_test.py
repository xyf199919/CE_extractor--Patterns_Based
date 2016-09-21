# -*- coding: UTF-8 -*- 

#######################################################################################
#--------------------------------- Function Introduce --------------------------------#
#######################################################################################
# This functions set intends to:
# 1. Added many 'print' statements into cmyPatternMatching.py in order to find errors. 

#######################################################################################
#---------------------------------- Global variable ----------------------------------#
#######################################################################################
import os
import nltk
import re
import string
import sys
import operator
import random
from cmyToolkit import *
from cmyPreprocess import *
from nltk.parse import stanford
from nltk.tree import *
from nltk.corpus import wordnet as wn
###---- stanford_parser java package ----  
os.environ['STANFORD_PARSER'] = 'E:/jars/stanford-parser.jar'  
os.environ['STANFORD_MODELS'] = 'E:/jars/stanford-parser-3.5.2-models.jar'  
###---- JAVA_HOME path ----
java_path = "E:\Program Files\Java\jdk1.8.0_45\bin\java.exe"  
os.environ['JAVAHOME'] = java_path  
###---- initiate a parser ---- 
parser = stanford.StanfordParser(model_path="E:\jars\englishPCFG.ser.gz")  
#--------- set some folder path ------------------
corpdir = os.path.join(os.getcwd(),"Corpus")
pkdir = os.path.join(os.getcwd(),"PK","DIC")
#--------- people hypernym set ------------------
PEOPLE = ('person','individual','someone','somebody','mortal','soul','being','human','hominid','humans','man','mankind')

#######################################################################################
#-------------------------------------- Classes --------------------------------------#
#######################################################################################

###---- 'Cause&Effect links pattern' class ----
class pattern:
    #--- tlist contains the name of all pattern types. It has 3 levels. 
    #--- use [self.tlist[0][tnum[0]-1],self.tlist[1][tnum[0]-1][tnum[1]-1],self.tlist[2][tnum[0]-1][tnum[1]-1][tnum[2]-1]] to visit
    tlist = ([
                 ['ADVERBIAL', 'PREPOSITIONAL', 'SUBORDINATION', 'CLAUSE-INTEGRATION'],
                 [['Anaphoric','Cataphoric'],['Adverbial','Postmodifying'],['Subordinator','Non-finite ing-clause','Correlative comparative'],['Rhematic link','Thematic link']],
                 [[['Implicit','Pronominal','Pronominal+Lexical'],['']],
                  [[''],['']],
                  [[''],[''],['']],
                  [['Clause-internal','Anaphoric pronominal subject','Anaphoric nominal subject','Non-anaphoric subject','Cleft constructions','Retrospective reinforcement','Mediating','Prospective:thematic first member','Prospective:rhematic first member'],['Anaphoric','Mediating']]
                 ],
               ])
    #--- ProcessPattern function using to parse the pattern_text into pattern_main_token and pattern_main_constraints
    def ProcessPattern(self,ptxt):
        main_token = [];
        constraints = [];
        ###--- split pattern_txt into words & delete the empty words ----
        pwords = DelEmptyString(ptxt.split(' '));
        ###--- divide the words into main_tokens and constraints ---
        i = 0;        
        while i < len(pwords):
            temp_main = [];
            temp_constraints = [];
            ###------- if current word is a constrain ----------
            while i < len(pwords):
                p = pwords[i];
                ### if current word start with '&', append it into temp constraints;
                if p[0] == '&':
                    temp_constraints.append(p);
                    i += 1;
                ### if current word start with '(', find the whole ignore pieces, append it into temp constraints
                elif p[0] == '(':
                    if p[-1] == ')':
                        temp_constraints.append(p);
                        i += 1;
                    else:
                        for j in range(i+1,len(pwords)):
                            p = p + ' ' + pwords[j];
                            if pwords[j][-1] == ')':
                                temp_constraints.append(p);
                                i = j +1;
                                break;
                else:
                    break;
            ###------ if current word is a main_tokens --------
            while i < len(pwords):
                p = pwords[i];
                if p[0] not in ['(','&']:
                ### ----- delete '/' ------
                    if '/' in p:
                        temp_main.append(DelEmptyString(p.split('/')));
                    else:
                        temp_main.append(p)
                    i += 1;
                else:
                    break;
            constraints.append(temp_constraints);
            if len(temp_main) > 0: 
                main_token.append(temp_main);
                
        return main_token, constraints;

    ###---- 'pattern' object initiation function ----    
    ###---- each 'pattern' object has 5 members:
    ###-------- pfreq: a int number, storing the frequency of a pattern ----- 
    ###-------- ptype: a 1D list witch containing 3 number, storing the 3-level type for each pattern
    ###-------- main_token: a at most 3D list, storing the main tokens for each pattern
    ###-------- constraints: a 2D list, storing the constian tokens for each pattern
    ###-------- cases: a 1D list, storing the example strings for each pattern
    def __init__(self,frequence,moresent,ptidx,ptxt,etxt):
        self.pfreq = frequence;
        self.moresent = moresent;
        self.ptype = ptidx;
        (self.main_token, self.constraints) = self.ProcessPattern(ptxt);
        self.cases = etxt;
    ###---- 'pattern' object equal justify function ----
    def __eq__(self,other):
        return (self.__class__ is other.__class__ and
                (self.pfreq, self.ptype, self.main_token, self.constraints) == (other.pfreq, other.ptype, other.main_token, other.constraints))    
    ###---- 'pattern' object self < other justify function ----
    def __lt__(self, other):
        self_mtlen = 0;
        other_mtlen = 0;
        self_cnslst = ListFlatten(self.constraints);
        other_cnslst = ListFlatten(other.constraints);
        self_cnslen = 0;
        other_cnslen = 0;
        
        for mt in self.main_token:
            self_mtlen += len(mt);
        for mt in other.main_token:
            other_mtlen += len(mt);
        for cns in self_cnslst:
            if cns[0]!= '(':
                self_cnslen += 1;
        for cns in other_cnslst:
            if cns[0]!= '(':
                other_cnslen += 1;
        
        if not isinstance(other, pattern):
            raise TypeError('Both the Comparing objects should be a object of pattern!')
        if self_mtlen != other_mtlen:
            return self_mtlen < other_mtlen;
        elif len(self.main_token) != len(other.main_token):
            return len(self.main_token) < len(other.main_token);
        elif self_cnslen != other_cnslen:
            return self_cnslen < other_cnslen;
        else:
            return self.pfreq < other.pfreq;

    __ne__ = lambda self, other: not self == other
    __gt__ = lambda self, other: not (self < other or self == other)
    __le__ = lambda self, other: self < other or self == other
    __ge__ = lambda self, other: not self < other

###---- 'Cause or Effect' class ----
class CorE:
    def __init__(self,parserTree,leaveSpan):
        self.PTree = parserTree;
        self.span = leaveSpan;
    
    def __eq__ (self,other):
        return (self.__class__ is other.__class__ and
                (self.span, self.PTree) == (other.span,other.PTree));

###---- 'Cause&Effect link' class ----
class CELink:
    def __init__(self,pt,parserTree,cause,effect):
        self.pt = pt;
        self.PTreelst = parserTree;
        self.cause = cause;
        self.effect = effect;
        self.sInfo = []; ### the Sent_class(see cmyPreprocess.py) object list constructing this CElink;
    
    def __eq__(self,other):
        return (self.__class__ is other.__class__ and
                (self.PTreelst, self.pt, self.cause, self.effect) == (other.PTreelst, other.pt, other.cause, other.effect));

#######################################################################################
#--------------------------- Some demonstration functions ----------------------------#
#######################################################################################
###---- show each pattern ----
def ShowPatterns(Patterns):
    for p in Patterns:
        if not isinstance(p, pattern):
            raise TypeError("ShowPatterns: This is not a pattern!");
        print str(p.pfreq)+"  "+str(p.main_token) +" ---- "+ str(p.constraints);
        #print p.cases;

###---- show cause or effect ----
def ShowCorE(c_e):
    if not isinstance(c_e,CorE):
        raise TypeError("ShowCorE: This is not a CorE!");
    print "--CorE_ParserTree:"
    print c_e.PTree;
    print "--CorE_LvsIdx:",c_e.span;

###---- show CElinks ----
def ShowCELink(celink):
    if not isinstance(celink,CELink):
        raise TypeError("ShowCorE: This is not a CElink!");
    print "Pattern:"
    ShowPatterns([celink.pt]);
    print "ParserTree:"
    for pt in celink.PTreelst:
        print pt;
    print "Cause:"
    ShowCorE(celink.cause);
    print "Effect:"
    ShowCorE(celink.effect);

def CElst2TXT():
    CEList =  Loadpickle(os.path.join(pkdir,'CEList.pk'))
    CorpusCEfp = os.path.join(os.getcwd(),'CheckTXT','CorpusCE_9.txt')
    CorpusCE = codecs.open(CorpusCEfp,'w','utf8')
    
    for i in range(len(CEList)):
        CorpusCE.write("************************************************************\n")
        CorpusCE.write("f%04d" %(i+1) +": Cause-Effect links\n")
        CorpusCE.write("************************************************************\n\n")
        CEset = CEList[i];
        for j in range(len(CEset)):
            CorpusCE.write("CASE: "+str(j+1)+'\n');
            ce = CEset[j];
            CorpusCE.write("Stag: ");
            for ceSentInfo in ce.sInfo:
                CorpusCE.write("%d " %ceSentInfo.Stag);
            CorpusCE.write("\n");
            CorpusCE.write("\tPattern: "+'%d' %ce.pt.pfreq + ' %s' %ce.pt.main_token+"----"+ ' %s' %ce.pt.constraints +'\n');
            sentTXT = [];
            for PT in ce.PTreelst:
                sentTXT.extend(PT.leaves());
            CorpusCE.write("\tsentTXT: "+ ' '.join(sentTXT)+'\n');
            CorpusCE.write("\tCause: " +' '.join(ce.cause.PTree.leaves())+'\n');
            CorpusCE.write("\tEffect: "+' '.join(ce.effect.PTree.leaves())+'\n\n');
    
    CorpusCE.close()
    return

#######################################################################################
#------------------------------- Pattern Process -------------------------------------#
#######################################################################################

###---- TXT2Patterns process the causal_links.txt into "pattern" type object list ----  
def TXT2Patterns():
    causaltxt = ReadFile(os.path.join(corpdir,'causal_links.txt'));
    causal_txt_lines = causaltxt.splitlines();
    Patterns = [];
    for txt in causal_txt_lines:
        ###---- if a line is a empty string, skip it ----
        if len(txt) == 0 or re.match(ur"[\s]+$",txt): 
            continue
        ###---- if a line started with '#', it is a comment line, skip it ----
        if re.match(ur"#", txt):  
            continue
        ###---- get the 3-level type for each pattern ----
        ptidx = [ int(i) for i in list((re.match(ur'(\d+) (\d+) (\d+) (\d+) (\d+)',txt)).groups())];
        ###---- get pattern text for each pattern ----
        ptxt = re.search(ur'(?<={)(.+)(?=})',txt).group(0);
        ###---- get example text list for each pattern ---- 
        etxt = re.findall(ur'(?<=\[)([^\]]+)(?=\])',txt)
        ###---- create a 'pattern' type object and append it into "Patterns" list ----
        Patterns.append(pattern(ptidx[0],ptidx[1],ptidx[2:],ptxt,etxt))
    Dumppickle(os.path.join(pkdir,'Patterns.pk'), Patterns)
    return Patterns

###---- Split the Patterns List by the length of main_token ----
def SptPtnlst_mtlen(Patterns,mtlen):
    SptPatterns = [[]];
    PtnSptDic,newIdx = {},1;
    
    ptidx = 0;
    while ptidx < len(Patterns):
        mtlst = ListFlatten(Patterns[ptidx].main_token);
        if len(mtlst) != mtlen:
            ptidx += 1;
            continue;
        mt = ' '.join(mtlst);
        if mt in PtnSptDic:
            SptPatterns[PtnSptDic[mt]].append(Patterns[ptidx]);
        else:
            PtnSptDic[mt],newIdx = newIdx,newIdx+1;
            SptPatterns.append([Patterns[ptidx]]);
        del Patterns[ptidx];
        
    while Patterns != []:
        mtlst = ListFlatten(Patterns[0].main_token);
        InsertFlag = False;
        for i in range(len(mtlst)-mtlen+1):
            mt = mtlst[i] if mtlen == 1 else ' '.join(mtlst[i:i+mtlen]);
            if mt in PtnSptDic:
                SptPatterns[PtnSptDic[mt]].append(Patterns[0]);
                InsertFlag = True;
                break;
        if not InsertFlag:
            SptPatterns[0].append(Patterns[0]);
        del Patterns[0];
    
    return SptPatterns,PtnSptDic;

###----- check whether two patterns list is same! ----
def Check_Ptnlst_Eq(Patterns,newPatterns):
    if len(Patterns) != len(newPatterns):
        return False;
    
    flag = True;
    for ptn in Patterns:
        if ptn not in newPatterns:
            flag = False;
    for ptn in newPatterns:
        if ptn not in Patterns:
            flag = False;
    return flag

###---- Order the Patterns list ----            
def OrderPatterns(Patterns,rvsflag):
    cmpfun = operator.attrgetter('pfreq');
    Patterns.sort(key = cmpfun, reverse = rvsflag);
    SptPatterns = [Patterns[:]];
    Spt_mtlst = [];
    ###---- Split the Patterns list by the length of main_tokens in SptSpan
    for SptSpan in range(1,3):
        tempSptPtns,tempSptDic = SptPtnlst_mtlen(SptPatterns[0], SptSpan);
        Spt_mtlst.extend(tempSptDic.keys());
        SptPatterns[0] = tempSptPtns[0];
        SptPatterns.extend(tempSptPtns[1:]);
    ###---- Sort each split pattern list separately ----
    for ptnlst in SptPatterns:
        ptnlst.sort(reverse = rvsflag);
    ###---- merge all split pattern list ----
    newPatterns = [];
    while SptPatterns != []:
        MaxfrqPtnlst = 0;
        Maxfrq = -1;
        for i in range(len(SptPatterns)):
            if SptPatterns[i][0].pfreq > Maxfrq:
                Maxfrq = SptPatterns[i][0].pfreq;
                MaxfrqPtnlst = i;
        newPatterns.append(SptPatterns[MaxfrqPtnlst][0]);
        del SptPatterns[MaxfrqPtnlst][0];
        if SptPatterns[MaxfrqPtnlst] == []:
            del SptPatterns[MaxfrqPtnlst];
    ###---- Check whether the new Patterns list after ordered lost or repeat any pattern ----
    if Check_Ptnlst_Eq(Patterns, newPatterns):
        Dumppickle(os.path.join(pkdir,'Patterns.pk'), newPatterns);
        return newPatterns;
    else:
        raise ValueError("OrderPatterns: The Patterns losing or repeat adding element after sort");
        return [];
 

### 'MainTokenRegExp' intend to: create regular expression list for all patterns
###---- in order to check whether the sentence contains a pattern's main_token ---
###---- notice that the capture group (.*) is in accordance with Patterns constraints ----
def MainTokenRegExp(Patterns):
    mtRegExpList = [];  ### main_token Regular Expression list
    for p in Patterns:
        ### current Regular Expression for current patterns\
        ### if current pattern only have one main_token, find the first appearance of this main_token ----
        if len(p.main_token) == 1 and len(p.main_token[0]) == 1:
            curRegExp = ur'(.*?)';
        ### else, try to match as much as the pattern can ---- 
        else:
            curRegExp = ur'(.*)'; 
        ### patterns' main_token are broken into pieces, each piece must be matched successive.
        for pi in range(len(p.main_token)):
            ###---- if current constraint pieces has a class constraint piece, add " " ----            
            for cp in p.constraints[pi]:
                if cp[0] != '(':
                    curRegExp = curRegExp + ur' ';
                    break;
            ###---- add current main_token pieces into current Regular Expression -- curRegExp ----
            for ti in range(len(p.main_token[pi])):
                if ti > 0:
                    curRegExp += ur' ';
                tokens = p.main_token[pi][ti];
                ### if current token is a string, add it into curRegExp directly
                if type(tokens) == str:
                    if tokens in ['.','?',':']:
                        curRegExp += '\\'.encode('utf-8');
                    curRegExp += tokens.encode('utf-8');
                ### if current token is a list, create a "no capture group" (?:token[0]|token[1]|...) for it
                else:
                    curRegExp = curRegExp + ur'(?:'
                    for tempt in range(len(tokens)): 
                        if tempt > 0:
                            curRegExp = curRegExp+ur'|';
                        if tokens[tempt] in ['.','?',':']:
                            curRegExp = curRegExp + '\\'.encode('utf-8');
                        curRegExp = curRegExp + tokens[tempt].encode('utf-8');
                    curRegExp = curRegExp + ur')';
            ###---- if pattern is ended with a main_token, stop add "(.*)" ----
            if len(p.main_token)==len(p.constraints) and pi == len(p.main_token)-1:
                break;
            ###---- if next constraint pieces has a class constraint piece, add " " ----            
            for cp in p.constraints[pi+1]:
                if cp[0] != '(':
                    curRegExp = curRegExp + ur' ';
                    break;
            ###---- if current main_token pieces is not the last one, add (.*?), else add (.*) ----
            if pi < len(p.main_token)-1:
                curRegExp = curRegExp + ur'(.*?)';
            else:
                curRegExp = curRegExp + ur'(.*)';

        mtRegExpList.append(re.compile(curRegExp,re.I)); ###re.I means ignore upper or lower cases
     
    Dumppickle(os.path.join(pkdir,'mtRegExpList.pk'), mtRegExpList);
    return mtRegExpList;

### 'CheckPatternsCases' intends to:
### 1. Get Patterns: pattern object list.
### 2. Get mtRegExtlst: the Regular Expression list constructed by each pattern's main_tokens
### 3. Check whether each pattern can cope with its cases.
### 4. Recoding CE links extracting by matching each pattern with its cases into './CheckTXT/PatternsTestRecoding.txt' file
def CheckPatternsCases():
    ###---- get Patterns and mtRegExplst ----
    Patterns = TXT2Patterns();
    Patterns = OrderPatterns(Patterns,True);
    mtRegExplst = MainTokenRegExp(Patterns);
   
    emptyTree = Tree('ROOT',[]);
    plen = len(Patterns);
    
    TestRecfp = os.path.join(os.getcwd(),'CheckTXT','PatternsTestRecoding.txt')
    TestRec = codecs.open(TestRecfp,'w','utf8')
    
    for pi in range(plen):
        pt = Patterns[pi]
        print "*****************************************************"
        print "Processing Pattern ", pi;
        ShowPatterns([pt]);
        print mtRegExplst[pi].pattern;
                
        PTset = [];
        for str in pt.cases:
            PTset.extend(parser.raw_parse(str)); 

        for pppt in PTset:
            CEcases = GettingCEcases([pt], [mtRegExplst[pi]], emptyTree, pppt, emptyTree);
            if CEcases == []:
                print "case : ",' '.join(pppt.leaves()),"cannot match!\n"
            else:
                print "%%%%%%%%%%%%%%%%%%%%%%CE cases!%%%%%%%%%%%%%%%%%%%%"
                for ce in CEcases:
                    ShowCELink(ce);
                    print;

    TestRec.close();
    
#######################################################################################
#-------------------- Stanford Parser-Tree Leave Span Index --------------------------#
#######################################################################################

###---- Given the main_tokens matched txt groups, find their according leave index in parser trees sentPT ----
###---- leaveIdx: a list, each element is a list containing 2 tuple, representing the start and end idx for each group pieces ----
###---- and each tuple contains 2 number: 1st number is the PT idx in sentPT; 2nd number means the leave idx in according PT ----   
def Find_leaves_Idx(ptn,sentTXT,groups,TXT_split):   
    leaveIdx=[];
    if (ptn.constraints)[0] == []: #and len(groups[0])==0:
        leaveIdx.append([(-1,-1),(-1,-1)]);
        del groups[0];
   
    for g in groups:
        g = g.strip();
        ### if current matching content g is a empty string, append a empty leave index span [(-1,-1),(-1,-1)] into leaveIdx
        if len(g) == 0:
            leaveIdx.append([(-1,-1),(-1,-1)]);
            continue;
        ### else, find the strings leave index span
        span = [];
        sg_Idx = sentTXT.index(g);
        eg_Idx = sg_Idx + len(g)-1;
        ptidx = 1;
        while ptidx < len(TXT_split):
            if sg_Idx <= TXT_split[ptidx][0]:
                span.append((ptidx-1,sentTXT[0:sg_Idx].count(' ')-TXT_split[ptidx-1][1]));
                break;
            ptidx += 1;
        while ptidx < len(TXT_split):
            if eg_Idx <= TXT_split[ptidx][0]:
                span.append((ptidx-1,sentTXT[0:eg_Idx].count(' ')-TXT_split[ptidx-1][1]));
                break;
            ptidx += 1;
        leaveIdx.append(span);       
        
    return leaveIdx;

###---- check whether a leave span index is legal ----
def checkLvsIdx(PTlst,LvsIdx,sp):
    ###---- index should be a nonegtive number 
    if LvsIdx[0][0] < 0 or LvsIdx[0][1] < 0 or LvsIdx[1][0] < 0 or LvsIdx[1][1] < 0:
        return False;
    ###---- start_leave_index should 'before' than end_leave_index
    if LvsIdx[0][0]*sp > LvsIdx[1][0]*sp:
        return False;
    if LvsIdx[0][0] == LvsIdx[1][0] and LvsIdx[0][1]*sp > LvsIdx[1][1]*sp:
        return False;
    ###---- start_leave_index and end_leave_index should be found in PTlst
    PTnum = len(PTlst)
    if LvsIdx[0][0] >= PTnum or LvsIdx[1][0] >= PTnum:
        return False;
    STlen = len(PTlst[LvsIdx[0][0]].leaves());
    ETlen = len(PTlst[LvsIdx[1][0]].leaves());
    if LvsIdx[0][1] >= STlen or LvsIdx[1][1] >= ETlen:
        return False;
    return True;

###---- move a leave index a step 'forward' ----
def movIdxForward(PTlst, Idx, sp):
    tempIdx = list(Idx);
    tempIdx[1] += sp;
    if sp > 0 and tempIdx[1] >= len(PTlst[tempIdx[0]].leaves()):
        tempIdx[0] += 1;
        tempIdx[1] = 0;
    elif sp < 0 and tempIdx[1] < 0:
        tempIdx[0] -= 1;
        if tempIdx[0] >= 0:
            tempIdx[1] = len(PTlst[tempIdx[0]].leaves())-1;
    return tuple(tempIdx)

###---- extend leave index span ----
def ExtendLvsIdx(curIdx, SL, EL, sp):
    ### sp < 0 means EL -(right)-> SL; sp > 0 means SL -(right)-> EL; need to adjust into SL -(right)-> EL
    if sp < 0: 
        SL,EL = EL,SL;
    ### if curIdx is a empty tuple, then [SL,EL] is its value;
    if len(curIdx) == 0:
        curIdx = [SL,EL]
    ### if sp >0 then expend curIdx forward
    elif sp > 0:
        curIdx = [curIdx[0],EL];
    ### if sp >0 then expend curIdx forward
    elif sp < 0:
        curIdx = [SL,curIdx[1]];
    
    return curIdx;

#######################################################################################
#------------------------ Stanford Parser-Tree process -------------------------------#
#######################################################################################

###---- Find the SubPT list in PTlst that between index_span (SL, EL) ---- 
def SubPTinSpan(PTlst,SL,EL,sp):
    ### if the span is not correct, showing error "MaxPTinSpan: The leave index span is not correct!":
    if not checkLvsIdx(PTlst, [SL,EL], sp):
        raise IndexError('The Parser Tree span [SL,EL] of PTlst is not correct!')
        return None, SL, EL;
    
    SubPTlst  = []; ### SubPTlst store the SubParserTree in span [SL,EL] 
    curPTIdx = SL[0];  ### curPTIdx store the current visit ParserTree Index in ParserTree list PTlst;
    curLvsIdx = SL[1]; ### curLvsIdx store the started current Leave Index in PTlst[curPTIdx] that we need to build a subPT 
    
    ###---- if (curPTIdx,curLvsIdx) still in leaves index span (SL,EL), continue build subPT ----
    while (curPTIdx*sp < EL[0]*sp) or ((curPTIdx == EL[0]) and curLvsIdx*sp <= EL[1]*sp):
        ### curSubPT_loc: the position of curLvsIdx_th leaves in PTlst[curPTIdx]
        curSubPT_loc = list(PTlst[curPTIdx].leaf_treeposition(curLvsIdx));  
        
        ###---- if get curSubPT's parent -> curParentPT has no leaves beyond span [(curPTIdx,curLvsIdx),EL] ----
        ###---- then backtrack, i.e. curSubPT = curParentPT ---- 
        while True:
            ###---- if curSubPT_loc is empty list, means curSubPT point to the ROOT of PTlst[curPTIdx], cannot continue backtrack ----  
            if curSubPT_loc == []:  
                break;
            ###---- get curParentPT_loc: the current Parent Parser Tree location; curParentPT: the current Parent Parser Tree----
            curParentPT_loc = curSubPT_loc[0:-1];
            if curParentPT_loc == []:
                curParentPT = PTlst[curPTIdx];
            else:
                curParentPT = PTlst[curPTIdx][curParentPT_loc];
            
            ###---- check whether curParentPT has child that beyond span [(curPTIdx,curLvsIdx),EL] ----
            ###---- if such a child is not exist, continue backtrack: curSubPT_loc = curParentPT_loc ----
            
            sibIdx = curSubPT_loc[-1] - sp; ### sibIdx: the sibling index of curSubPT in curParentPT at -sp direction
            ###---- if such a sibling is not exist ----
            if sibIdx < 0 or sibIdx >= len(curParentPT): 
                ###---- check whether curSubPT has leaves beyond EL ----
                (tempPTIdx,tempLvsIdx) = movIdxForward(PTlst,(curPTIdx,curLvsIdx), (len(curParentPT.leaves())-1)*sp);
                if (tempPTIdx == EL[0]) and tempLvsIdx*sp > EL[1]*sp: ### if it has leaves beyond EL, stop backtracking
                    break;
                else:  ### if its leaves all in span [(curPTIdx,curLvsIdx),EL], continue backtrack
                    curSubPT_loc = curParentPT_loc; 
            ###---- if such a sibling exist, then stop backtracking ----
            else:
                break;
        ###---- Get final curSubPT, add it into SubPTlst ----
        if curSubPT_loc == []:
            curSubPT = PTlst[curPTIdx];
        else:
            curSubPT = PTlst[curPTIdx][curSubPT_loc];
        SubPTlst.append(curSubPT);     
        ###---- Get next start subPT leave index (curPTIdx,curLvsIdx) ---- 
        if isinstance(curSubPT,Tree):
            (curPTIdx,curLvsIdx) = movIdxForward(PTlst,(curPTIdx,curLvsIdx), len(curSubPT.leaves())*sp);
        else:
            (curPTIdx,curLvsIdx) = movIdxForward(PTlst,(curPTIdx,curLvsIdx), sp);    
    ###---- If there is only one SubPT in SubPTlst, return it; else build a new ParserTree Tree('ROOT',subPTlst) ----
    if len(SubPTlst) == 1:
        return SubPTlst[0];
    elif sp < 0:
        return Tree('ROOT',SubPTlst[::-1]);
    else:
        return Tree('ROOT',SubPTlst);

###---- if subPT's label doen't satisfy regexp and subPT only has one child, move subPT downward and continue the check ---- 
def PTMoveDownward(subPT,regexp = ur'',flag = False):
    while not flag and isinstance(subPT, Tree): 
        if regexp != ur'':
            flag = (True if re.match(regexp, subPT.label()) else False);
        if flag or len(subPT) != 1 or not isinstance(subPT[0], Tree):
            break;
        subPT = subPT[0];
    return flag, subPT;

#######################################################################################
#------------------------ Checking a Pattern Constrain piece -------------------------#
#######################################################################################
###----------- Get the hypernym's lemma_name of str in WordNet ----
def GetHyperNames(str):
    hypername = [];
    for synset in wn.synsets(str):
        hyperset = synset.hypernyms()
        for hs in hyperset:
            hypername.extend( hs.lemma_names())
    return hypername

###---- checkClass use to check whether a parser-tree can match a class, i.e. '&' ----
def checkClass(subPT, cp, SL, EL, sp, cIdx, eIdx):
    flag = False;
    poslst = subPT.pos(); ### poslst is a list of tuple like (pos, word)
    leafTXT = (' '.join(subPT.leaves())).strip().lower();
    
    if len(cp) == 0:
        raise SyntaxWarning("checkClass: Current class constraint pieces \'"+cp+"\' is empty");
        flag = False;
    elif cp[0] == '-' and cp != '--':
        if re.match(ur'-&.*',cp):
            tempflag,tempcIdx,tempeIdx = checkClass(subPT, cp[1:], SL, EL, sp, cIdx, eIdx);
            flag = not tempflag;
        else:
            flag = not (leafTXT == cp[1:]);
    elif cp[0] != '&':
        flag = (leafTXT == cp);
    elif cp == '&ClauseHead':
        flag = (leafTXT in ['that','whether','if','what', 'whatever', 'who', 'whoever', 'whom', 'whose', 'which','when', 'where', 'how', 'why']);
    elif cp == '&THIS':
        flag = (leafTXT in ['this','that','these','those','it','which']);
    elif cp == '&this':
        flag = (leafTXT in ['this','that','these','those']);
    elif cp == '&ADJ':
        flag = (leafTXT in ['direct', 'same', 'main', 'seperate', 'final', 'alone', 'important', 'major', 'key', 'biggest', 'possible', 'only', 'primary']);
    elif cp == '&adj':
        flag = True;
        for pos in poslst:
            if not re.match('JJ.*',pos[1]):
                flag = False;
                break;
    elif cp == '&ADV':
        flag = (leafTXT in ['just', 'also', 'only', 'merely', 'all', 'alone', 'often', 'simply']);
    elif cp == '&adv':
        flag = True;
        for pos in poslst:
            if not re.match('RB.*',pos[1]):
                flag = False;
                break;    
    elif cp == '&CAN':
        flag = (leafTXT in ['can', 'could', 'may', 'might', 'will', 'would', 'must', 'should', 'ought to']);
    elif cp == '&BE':
        flag = (leafTXT in ['be', 'being', 'been', 'have been','is', 'am', 'are', 'was', 'were']);
    elif cp == '&AND':
        flag = (leafTXT in ['and', 'but', 'so', 'also']);
    elif cp == '&NUM':
        flag = (True if re.match(ur'CD.*', subPT.label(), ) else False) or (leafTXT in ['a','an','several','a few','some', 'many','half']);
    elif cp == '&ONE':
        flag = (leafTXT in ['the','a','an','one','another']);
    elif cp == '&OF':
        flag = (leafTXT in ['one of','part of']);
    elif cp == '&MODNUM':
        flag = (leafTXT in ['at least','at most']);
    elif cp == '&N':
        flag = (True if re.match(ur'NN.*', subPT.label()) else False);
    elif cp == '&V':
        flag = (True if re.match(ur'VB.*', subPT.label()) else False);
    elif cp == '&NP':
        ###---- check whether subPT is labeled start with 'N' ----
        flag,subPT = PTMoveDownward(subPT, ur'N.*', flag)
        ###---- check whether subPT is only consisted by 'NP','PP','IN' ----
        if not flag and isinstance(subPT,Tree):
            countNP = 0;
            for cursubPT in subPT:
                ttflag,cursubPT = PTMoveDownward(cursubPT);
                flag = isinstance(cursubPT,Tree) and (re.match(ur'N.*',cursubPT.label()) or cursubPT.label() in ['DT','PP','IN','CC']);
                if not flag:
                    break;
                if re.match(ur'N.*',cursubPT.label()):
                    countNP += 1;
            flag = flag and (countNP > 0) and re.match(ur'N.*', subPT[0].label()) and subPT[-1].label() != 'CC'                 
    elif cp == '&V-ing':
        while not flag and isinstance(subPT, Tree):
            flag = (True if subPT.label()=='VP' and ((poslst[0][1] == 'VBG') or (poslst[0][1] in ['ADVP','RB','RBR','RBS'] and poslst[1][1] == 'VBG')) else False);
            if flag or len(subPT) > 1:
                break;
            subPT = subPT[0];

    elif cp == '&TODO':
        while not flag and isinstance(subPT, Tree): 
            flag = (True if subPT.label()=='VP' and ((poslst[0][1] == 'TO') or (poslst[0][1] in ['ADVP','RB','RBR','RBS'] and poslst[1][1] == 'TO')) else False);
            if flag or len(subPT) > 1:
                break;
            subPT = subPT[0];
    elif cp in ['&Clause','&C','&R']:
        ###---- subPT is a sentence judged by Stanford-Parser ----
        ###---- if subPT only has one child, move downward ---- 
        flag,subPT = PTMoveDownward(subPT,ur'S.*',flag);
        ###---- if subPT is not a sentence judged by Stanford-Parser ----
        if (not flag) and isinstance(subPT,Tree):
            ###---- if subPT only contains one words or subPT is a noun phrase judged by stanford-parser, it cannot be a sentence ----
            if re.match(ur'N.*',subPT.label()) or len(subPT.leaves()) == 1:
                flag = False;
            else:
            ###---- if all subPT's children's label are 'S.*' and 'CC' ----
                for cursubPT in subPT:
                    flag = isinstance(cursubPT,Tree) and (re.match(ur'S.*', cursubPT.label()) or cursubPT.label() in ['CC','.',',',':']);
                    if not flag:
                        break;
            ###---- else if one of subPT's children is labeled with 'V.*'  ----
                if not flag:
                    for cursubPT in subPT:
                        flag,cursubPT = PTMoveDownward(cursubPT, ur'(?:VP|VB$|VBZ|VBP|VBN|VBD)', flag);
                        if flag:
                            break;
        ###---- if subPT is clause and cp is &C or &E, should change cause or effect index--cIdx,eIdx ----
        if flag and cp == '&C':
            print "cIdx:",cIdx;
            cIdx = ExtendLvsIdx(cIdx, SL, EL, sp);
            print "cIdx:",cIdx;
        if flag and cp == '&R':
            print "eIdx:",eIdx;
            eIdx = ExtendLvsIdx(eIdx, SL, EL, sp);
            print "eIdx:",eIdx;
    else:
        raise SyntaxWarning("checkClass: Current class constraint pieces \'"+cp+"\' have never seen!");
        flag = False;
    return flag,cIdx,eIdx;
        

###---- checkAddition use to check whether the parser-tree can match the constraints starting and ending with '@' ----
def checkAddition(subPT, cp, SL, EL, sp, cIdx, eIdx):
    flag = False;

    if len(cp) == 0:
        raise SyntaxWarning("checkAddition: Current addition constraint pieces \'"+cp+"\' is empty");
        flag = True;
    elif cp == 'C':
        flag = True;
        print "cIdx:",cIdx;
        cIdx = ExtendLvsIdx(cIdx, SL, EL, sp);
        print "cIdx:",cIdx;
    elif cp == 'R':
        flag = True;
        print "eIdx:",eIdx;
        eIdx = ExtendLvsIdx(eIdx, SL, EL, sp);
        print "eIdx:",eIdx;
    elif cp == 'Complete':
        ###---- if subPT is a sent judged by stanford-parser, i.e. subPT's label is started with S, set flag = True ----
        ###---- if subPT's label doesn't start with S, and subPT only has one child, move downward ----
        flag,subPT = PTMoveDownward(subPT, ur'S.*') 
        ###---- if subPT's label cannot start with S, check whether subPT contains '.' between words ----
        if not flag:
            for i in range(len(subPT)):
                flag = isinstance(subPT[i],Tree) and [True,subPT[i].label() != '.'][i!=len(subPT)-1];
                if not flag:
                    break;
        ###---- if subPT cannot pass above check, re-parse the subPT's text to generate a new parser-tree ----
        ###---- if new parser-tree is a sent judged by stanford-parser, and has object and predicate ----
        if flag:
            subPT = (parser.raw_parse(' '.join(subPT.leaves()))).next();
            flag,subPT = PTMoveDownward(subPT, ur'S.*');
            print "new subPT:"
            print subPT
            ###---- If reconstructed subPT is a sentence, check whether it has N.* and V.* and N.* is before V.* ----
            try:
                cursubPT_taglst = [cursubPT.label() for cursubPT in subPT];
            except AttributeError:
                flag = False;
            if flag:    
                countNP,NPloc_1st = 0,-1;
                countVP,VPloc_1st = 0,-1;
                for cc in range(len(cursubPT_taglst)):
                    if re.match(ur'N.*', cursubPT_taglst[cc]):
                        if countNP == 0:
                            NPloc_1st = cc;
                        countNP += 1;
                    elif re.match(ur'V.*', cursubPT_taglst[cc]) and cursubPT_taglst[cc] != ur'VBG':
                        if countVP == 0:
                            VPloc_1st = cc;
                        countVP += 1;
                flag = (countNP > 0) and (countVP > 0) and (NPloc_1st < VPloc_1st);

    elif cp == 'NCTime':
        POS = subPT.pos();
        for curpos in POS:
            if re.match(ur'N.*',curpos[1]):
                hypername = GetHyperNames(curpos[0])
                for hn in hypername:
                    if re.match(ur'time.*', hn) or re.match(ur'.*time$',hn):
                        return flag,cIdx,eIdx;
        flag = True;
    elif cp == 'NCPeople':
        POS = subPT.pos();
        for curpos in POS:
            if curpos[1] == 'PRP':
                return flag,cIdx,eIdx;
            if re.match(ur'N.*',curpos[1]):
                tempstr = curpos[0]
                Timers = 4; 
                while Timers > 0 :
                    hypername = GetHyperNames(tempstr)
                    if not len(hypername):
                        break;
                    for hn in hypername:
                        if hn in PEOPLE:
                            return flag,cIdx,eIdx; 
                    tempstr = hypername[0];
                    Timers -= 1; 
        flag = True;
    else:
        raise SyntaxWarning("checkAddition: Current addition constraint pieces \'"+cp+"\' have never seen!");
        flag = True; 
    
    return flag,cIdx,eIdx;

###---- check whether the PTlst in span [SL,tempEL] can satisfy the class constraint pieces cp ----
def Check_cp_APlst(PTlst,cp,APlst,SL,tempEL,EL,sp,cIdx,eIdx):
    ###--- check if tempEL is still inside the span [SL,EL] ----
    if not checkLvsIdx(PTlst, [tempEL,EL], sp):
        return False,EL,cIdx,eIdx;
    ###---- subPT : the subParserTree in span (SL, tempEL) ---- ###---- subPT : the subParserTree in span (SL, tempEL) ---- 
    subPT = SubPTinSpan(PTlst,SL,tempEL,sp);
    print "cur_cp:",cp;
    print "curSubPT:",subPT;
    print "curLvsSpan:",[SL,tempEL];
    ###---- check whether parser tree subPT can satisfy cp ----
    flag,cIdx,eIdx = checkClass(subPT, cp, SL, tempEL, sp, cIdx, eIdx);
    ###---- if subPT cannot satisfy cp or APlist, return False and remain the original EL ----
    if not flag:
        return False,EL,cIdx,eIdx;
    ###---- if subPT can satisfy a cp, check whether it can satisfy cases in APlst ---- 
    for ap in APlst:
        flag,cIdx,eIdx = checkAddition(subPT, ap, SL, tempEL, sp, cIdx, eIdx);
        if not flag:
            return False,EL,cIdx,eIdx;
    ###---- if subPT can satisfy cp and APlst, return True and return tempEL as newEL ----
    return True,tempEL,cIdx,eIdx;



#######################################################################################
#--------------------------------- Pattern Matching ----------------------------------#
#######################################################################################
### 'MatchingClassPiece' function intend to:
### 1. split a constraint piece start with '&' into class_condition_list CPlst and additional_condition_list APlst
### 2. create subtrees that contained by (PTlst,curLvsIdx) 
### 3. check whether one of these subtrees can matching a cp in CPlst and can matching all ap in APlst 
###    1) if exist, i.e. the '&' constraint piece can be successfully matched,  then return 'True' and modify the current_leaves_span_index curLvsIdx
###    2) if not exit, return false and return original curLvsIdx.
### Notices:
### 1. Adopting maximum matching mechanism, i.e., constraint = &NP , string = He feed these beautiful dogs, we need to find "these beautiful dogs" instead of 'dogs','beautiful dogs'. 
### 2. in this matching mechanism may create the cause and effect leaves span, '&C','&R','&NP@C@','&V-ing@C@' ...
def MatchingClassPiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx):
    ###---- if current leaves index span is illegal, return False ----
    if not checkLvsIdx(PTlst, curLvsIdx, sp):
        print "current constraint pieces:",consp
        print "current leave span is illegal!"
        return False, curLvsIdx, cIdx, eIdx;
    
    flag = False;
    ###---- get class condition pieces list--> CPlst; additional conditional pieces list--> APlst -----
    if len(consp and '@') > 0:  ### if current constraint pieces 'consp' contains additional condition i.e. '@C@'
        templst = DelEmptyString(re.split('@+',consp));
        CPlst = DelEmptyString(re.split('/+',templst[0]));
        APlst = templst[1:]; 
    else:    ### if current constraints pieces 'consp' not contains additional condition.
        CPlst = DelEmptyString(re.split('/+',consp));
        APlst = [];
    SL = curLvsIdx[0];
    EL = curLvsIdx[1];
    minusflag = False;
    print "\n****************************"
    print "current constraint pieces:",consp; 
    print "CPlist:",CPlst
    print "APlist:",APlst
    print "LvsSpan:",[SL,EL]
    print "-------check process --------"
    ###---- if has not found subST satisfy consp, and curLvsIdx is a legal leave span ----
    ###---- get new subPT in span [SL,EL] ---- 
    for cp in CPlst:
        ###---- if current cp is minus constraint as '-&adj', if it cannot be processed correctly, stop check remaining cp ----
        if cp[0] == '-' and cp != '--':
            minusflag = True;
            flag,ttEL,cIdx,eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, SL, EL, sp, cIdx, eIdx);  
            if not flag:
                break;
        ###----if cp is the class_constraint_pieces that only cover one word ----
        elif cp[0] != '&' or cp in ['&THIS','&this','&ClauseHead','&ADJ','&ADV','&AND','&ONE']:
            flag,EL,cIdx,eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, SL, EL, sp, cIdx, eIdx);
        ###----if cp is the class_constraint_pieces that at most cover two word ----
        elif cp in ['&CAN','&BE','&OF','&MODNUM']:
            for inc in range(0,2):
                tempEL = movIdxForward(PTlst, SL, sp*inc);
                flag,EL,cIdx,eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx); 
                if flag:
                    break;
        ###---- if cp is the class_constraint_pieces that doesn't sure cover how many words, but all of them must be the same kind of label ----
        elif cp in ['&adj','&adv','&N','&V','&NUM']:
            havematched, lastMatchedEL, tempEL = False, SL, SL;
            while checkLvsIdx(PTlst, [tempEL,EL], sp):
                tempflag,newEL,cIdx,eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx);
                if not tempflag:
                    break;
                havematched, lastMatchedEL = True, newEL;
                tempEL = movIdxForward(PTlst, tempEL, sp);
            if havematched:
                flag, EL = True, lastMatchedEL;
        ###---- if cp is the class_constraint_pieces that doesn't sure cover how many words, and their label may be different ----
        elif cp in ['&NP','&V-ing','&TODO']:
            ###---- skip the punctuation symbol at the start position ----
            while checkLvsIdx(PTlst, [SL,EL], sp) and SubPTinSpan(PTlst, SL, SL, sp).label() in ['.',',',':']:
                SL = movIdxForward(PTlst, SL, sp);
            ###---- start matching process ----
            havematched, lastMatchedEL, tempEL = False, SL, SL;
            while checkLvsIdx(PTlst, [tempEL,EL], sp):
                tempflag,newEL,cIdx,eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx);
                if tempflag:
                    havematched, lastMatchedEL = True, newEL;
                tempEL = movIdxForward(PTlst, tempEL, sp);
            if havematched:
                flag, EL = True, lastMatchedEL;
        ###---- if cp is a class_constraint_piece that covers a clause, matched by decreasing the span ----
        else:
            tempEL = EL;
            while (not flag) and checkLvsIdx(PTlst, [SL,tempEL], sp):        
                flag,EL,cIdx,eIdx = Check_cp_APlst(PTlst, cp, APlst, SL, tempEL, EL, sp, cIdx, eIdx);
                tempEL = movIdxForward(PTlst, tempEL, -sp);
        ###----if cp is not a minus constrant and can be matched,  stop check the remaining pieces in CPlist ----
        if flag and not minusflag:
            break; 
    ###---- we found subPT can match CPlst and APlst, and CPlst not contain minus constraints ----
    print "##############current matching Results################"
    ###---- then move EL a step forward, return 'True' and next LvsIdx ----
    if flag and not minusflag:
        EL = movIdxForward(PTlst, EL, sp);
        print consp,"can be matched!"
        print "new span:",[EL,curLvsIdx[1]],'\n';
        return flag,[EL,curLvsIdx[1]],cIdx,eIdx;
    ###---- if CPlist is a minus constraint list and can be matched correctly, return True and original span as next span ----
    elif flag and minusflag:
        print "consp is a minus class constraint, it can be processed correctly!"
        return flag,curLvsIdx,cIdx,eIdx;
    ##---- if cannot match, then return 'False' ----
    print consp,"not match!!!\n"
    return False, curLvsIdx, cIdx, eIdx;


### 'MatchingIgnorePiece' intends to:
### 1. check whether a Ignore constraint piece, i.e. the constraints start with '(' and end with ')', is legal. 
### 2. split the Ignore constraint piece into a list of class constraint pieces and small Ignore constraint pieces
### 3. Get sub_ParserTrees inside leaves span curLvsIdx, check whether they can match each piece we got in step 2:
###    1) If can match, return True and modify the next under checking leaves_span
###    2) If cannot, return False and the current checking leaves_span;
def MatchingIgnorePiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx):
    print "\n****************************"
    print "current constraint pieces:",consp; 
    print "LvsSpan:",curLvsIdx
    print "-------check process --------"
    ###---- current constraint pieces 'consp' start with '(' and end with ')',delete '(',')' ----
    while len(consp)>1 and consp[0] == '(' and consp[-1] == ')':
        consp = consp[1:-1];
    ### if '(' and ')' does not paired up at the begin and end of consp, raise error "'(' and ')' doesn't paired up!"
    if re.match(ur'\([^\)]*$', consp) or re.match(ur'[^\(]*\)$', consp):
        raise SyntaxError("When checking ignore constrains: '(' and ')' doesn't paired up!")
        return False,curLvsIdx,cIdx,eIdx;
    ###---- get class condition pieces list--> Iglst ----
    Iglst = DelEmptyString(re.split(' ',consp));
    i = 0;
    while i < len(Iglst):
        lenIglst = len(Iglst);
        if Iglst[i][0] == '(':
            j = i;
            while j < lenIglst and Iglst[j][-1] != ')':
                j += 1;
            tempIglst = Iglst[i:j+1] if j < lenIglst else Iglst[i:lenIglst];
            Iglst[i] = ' '.join(tempIglst);
            k = (j - i) if j < lenIglst else (j-i-1);
            while k > 0:
                del Iglst[i+1];
                k = k - 1;
        i = i + 1;
    ###---- Matching Process ----
    SL = curLvsIdx[0];
    EL = curLvsIdx[1];
    ###---- for each ig in Iglst, check whether PTlst[SL,EL] on can match it, if can change SL to create new Leaves Index Span ----
    for ig in Iglst:
        if len(ig) > 0 and ig[0] == '(':
            flag,tempIvsIdx,cIdx,eIdx = MatchingIgnorePiece(PTlst, ig, [SL,EL], sp, cIdx, eIdx);
        else:
            flag,tempIvsIdx,cIdx,eIdx = MatchingClassPiece(PTlst, ig, [SL,EL], sp, cIdx, eIdx);
        if flag:
            SL = tempIvsIdx[0];
            EL = tempIvsIdx[1];
            print "(",ig,") can be matched!"
            print "new span:",[SL,EL];
        elif ig[0] == '-' and not flag:
            print '(',ig,') cannot be satisfied, return false'; 
            return False,[SL,EL],cIdx,eIdx;
        else:
            print "(", ig, ") not find!!!"
    return True,[SL,EL], cIdx, eIdx;
    
### 'MatchingConstraints' intend to:
### check whether the parser tree satisfied Patterns[m]'s constraints
###    1) if satisfied, return True, whole sent parser tree(list), cause(CorE), effect(CorE) ----
###    2) if unsatisfied, return False,[],None,None ----
def MatchingConstraints(PTlst, pattern, leavesIdx):
    finalCheck = True;
    cIdx = [];
    eIdx = [];
    C_cons = re.compile(ur'&C.*');
    R_cons = re.compile(ur'&R.*');
    Cons = pattern.constraints; ### pattern's constraints list
    for i in range(len(Cons)):
        curCons = Cons[i]; ### current constraint pieces, a list
        curLvsIdx = leavesIdx[i]; ### current constraint's matching text start_leaf and end_leaf in PTlst;
        sp = 1;
        ###---- current constraint is the first constraint, it should be checked reversely, or----
        if i == 0:
            curCons = curCons[::-1];
            curLvsIdx = curLvsIdx[::-1]; 
            sp = -sp;
        ###---- current constraint is start with &C or &R and not end with &C or &R, it should be checked reversely ----
        if  len(curCons) > 1 and (C_cons.match(curCons[0]) or R_cons.match(curCons[0])) and \
            not C_cons.match(curCons[-1]) and not R_cons.match(curCons[-1]):
            curCons = curCons[::-1];
            curLvsIdx = curLvsIdx[::-1]; 
            sp = -sp;
        ###---- for each curCons piece, check whether PTlst can fit it ----         
        for consp in curCons:
            if consp[0] == '&':
                finalCheck, curLvsIdx, cIdx, eIdx = MatchingClassPiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx);
            elif consp[0] == '(':
                finalCheck, curLvsIdx, cIdx, eIdx = MatchingIgnorePiece(PTlst, consp, curLvsIdx, sp, cIdx, eIdx);
            else:
                raise SyntaxWarning("MatchingConstraints: Current constraint pieces \'"+consp+"\' have never seen!");
            ###---- Once PTlst cannot fit the curCons piece, whole constraints matching fall, stop matching ---- 
            if not finalCheck:
                break;
        ###---- if has find unmatched constraints, stop check remain constraits ----
        if not finalCheck:
            break;
    return finalCheck,cIdx,eIdx;


#######################################################################################
#--------------------------------- Build CE links ------------------------------------#
#######################################################################################
### 'GettingCEcases' intend to: Build CE links for a ParserTree using patterns
### Input:
###    1. Patterns: a list of pattern we can choose.
###    2. mtRegExpList: a list of re.compile() object constructed by main_tokens of each pattern, is used to match curPT's text and break it into groups.
###    3. curPT: current processing stranford parser tree.
###    4. prePT, nextPT: the pre or next parser tree for curPT to serve as additional material, because some patterns are designed to deal with 2 adjacent sentences.
### Output:
###    CEcases: a list of CElink object that we can extracted from curPT additional with its pre and next parser-tree.
def GettingCEcases(Patterns,mtRegExpList,prePT,curPT,nextPT):
    CEcases = [];
    plen = len(Patterns);
    preTXT = ((' '.join(prePT.leaves())).lower()).strip();
    pTxtLen = len(preTXT);
    pLvsLen = len(prePT.leaves());
    curTXT = ((' '.join(curPT.leaves())).lower()).strip();
    cTxtLen = len(curTXT);
    cLvsLen = len(curPT.leaves());
    nextTXT = ((' '.join(nextPT.leaves())).lower()).strip();
    nTxtLen = len(nextTXT);
    nLvsLen = len(nextPT.leaves());
    ###---- create sentST, sentTXT, sentTXTidx ----
    ### sentPT: adjacent Parser Tree that may formed a CE links
    ### sentTXT: convert the sentST' leaves into a string in sequence
    ### sentTXTidx: store the end_index of each parser_tree_leaves string in sentTXT, in order to check current matching group belonging to which parser_tree
    ### i.e., sentTXT_split_idx[1][0] < txtidx < sentTXT_split_idx[1][1], then txtidx belonging to sentPT[1][1], i.e. curPT
    sentPT = [[curPT],
              [prePT,curPT],
              [curPT,nextPT]
             ];
    sentTXT = [curTXT, 
               preTXT + [u' ',u''][pTxtLen == 0] + curTXT, 
               curTXT + [u' ',u''][nTxtLen == 0] + nextTXT
              ];
    sentTXT_split_idx = [[(0,0),(cTxtLen,cLvsLen)],
                         [(0,0),(pTxtLen,pLvsLen),(pTxtLen+cTxtLen,pLvsLen+cLvsLen)],
                         [(0,0),(cTxtLen,cLvsLen),(cTxtLen+nTxtLen,cLvsLen+nLvsLen)]
                        ];
    emptyTree = Tree('ROOT',[]);

    ###---- for each pattern ----
    for m in range(plen):
        ###---- check whether current Sent satisfied Patterns[m]'s main token ----
        if Patterns[m].constraints[0] == []:
            mtResult = mtRegExpList[m].match(curTXT);
        else:
            mtResult = mtRegExpList[m].match(ur' '+curTXT);
        finalCheck = False 
        ###---- If satisfied Patterns[m]'s main token ----
        if mtResult:
            print "*****************************************************"
            print "Processing Pattern ",m+1;
            ShowPatterns([Patterns[m]]);
            print "curmtRegExp:",mtRegExpList[m].pattern
            print "curTXT:",curTXT
            print
            for i in range(3):
                ###---- if current pattern cannot cover more than one sentence ----
                # or (i == 2 and len(Patterns[m].main_token) == len(Patterns[m].constraints)):
                if i > 0 and not Patterns[m].moresent:
                    break;
                ###---- Get constraints coordinated text tuples consTxtTup ----
                consTxtTup = [mtstr.strip() for mtstr in mtResult.groups()];
                if i == 1:
                    consTxtTup[0] = preTXT + u' ' + consTxtTup[0];
                elif i == 2:
                    consTxtTup[-1] = curTXT[curTXT.index(consTxtTup[-1]):] + [u' ',u''][nTxtLen == 0] + nextTXT;
                print sentTXT[i]
                print sentPT[i]
                print consTxtTup;
                ###---- Get the leave spans for each constrain piece ----
                leavesIdx = Find_leaves_Idx(Patterns[m],sentTXT[i],consTxtTup,sentTXT_split_idx[i]);
                print leavesIdx;
                finalCheck, cIdx, eIdx = MatchingConstraints(sentPT[i],Patterns[m],leavesIdx)
                print finalCheck,cIdx,eIdx
                print
                ###---- if it is satisfied, create CELink object and append it into current CE set ----
                if finalCheck:
                    if cIdx == []:
                        cause = CorE(emptyTree,cIdx);
                    else:
                        cause = CorE(SubPTinSpan(sentPT[i], cIdx[0], cIdx[1], 1),cIdx);
                    if eIdx == []:
                        effect = CorE(emptyTree,eIdx);
                    else:
                        effect = CorE(SubPTinSpan(sentPT[i], eIdx[0], eIdx[1], 1),eIdx);
                    CEcases.append(CELink(Patterns[m],sentPT[i],cause,effect))
                    if len(sentPT[i]) == 1:
                        CEcases.extend(GettingCEcases(Patterns,mtRegExpList,emptyTree,cause.PTree,emptyTree))
                        CEcases.extend(GettingCEcases(Patterns,mtRegExpList,emptyTree,effect.PTree,emptyTree))
                    break;
        if finalCheck:
            break;
    return CEcases;

### 'CElinksForCorpus' intend to: create a CEList for the whole Corpus.
### Output:
###    CEList: CE Link set list for the whole corpus and each member means the CE Link set for a single paper  
def CElinksForCorpus():
    ###---- get pattern list ----
    Patterns = TXT2Patterns();
    Patterns = OrderPatterns(Patterns,True);
    ###---- get mtRegExplist(main_token RegExp List) for all patterns ----
    mtRegExpList = MainTokenRegExp(Patterns);
    ###---- CEList store the CElinks for all the corpus ----
    CEList = [];
    ###---- get paper object list of the corpus ----
    FList = Loadpickle(os.path.join(pkdir,'PaperList.pk'));
    ###---- For each file, Getting causal sentences ----
    for curfile in FList:
        cursentlst = curfile.S_list;
        slen = len(cursentlst);  ### the number of sentences in current file
        curCEset = [];

        print "*****************************************"
        print "Processing file:",curfile.Ftag;
        
        for s in range(slen):
            sent = cursentlst[s];
            emptyTree = Tree('ROOT',[]);
            if sent.PTree == []:
                continue;
            print "sentence: ",sent.Stag;
            ### we have checked that each sentence in the corpus is parsed into at most one parser-tree
            curPT = sent.PTree[0]; 
            prePT = emptyTree if s < 1 or cursentlst[s-1].PTree == [] else cursentlst[s-1].PTree[0];
            nextPT = emptyTree if s > slen-2 or cursentlst[s+1].PTree == [] else cursentlst[s+1].PTree[0];
            sentCEset = GettingCEcases(Patterns,mtRegExpList,prePT,curPT,nextPT);
            for sentCE in sentCEset:
                if len(sentCE.PTreelst) == 1:
                    sentCE.sInfo = [sent];
                elif sentCE.PTreelst[0] == sent.PTree[0]:
                    sentCE.sInfo = [sent,cursentlst[s+1]];
                else:
                    sentCE.sInfo = [cursentlst[s-1],sent];
            curCEset.extend(sentCEset);
            ###---- append current files CE set into whole CE set list ----
        print
        print "Length of CEset for current file:",len(curCEset)
        print
        CEList.append(curCEset);
    Dumppickle(os.path.join(pkdir,'CEList.pk'), CEList)
    return CEList;

#######################################################################################
#---------------------------------- Main function -- ----------------------------------#
#######################################################################################
if __name__ == "__main__":
    CElinksForCorpus()
#     sentTXT = 'Discovering , managing , and utilizing such knowledge are advanced services of the e-science knowledge grid environment . The knowledge flow network implicit in the citation network consists of knowledge flows between nodes that process knowledge , including resoning , fusing , generalizing , inventing , and problem solving , by authors and co-authors .';
#     sentPTItr = parser.raw_parse(sentTXT);
#     sentPT = [];
#     while True:
#         try:
#             sentPT.append(sentPTItr.next());
#         except StopIteration:
#             break;
# 
#     Patterns = TXT2Patterns();
#     Patterns = OrderPatterns(Patterns,True);
#     mtRegExplst = MainTokenRegExp(Patterns);  
#     CheckPatternsCases()  
# #     ShowPatterns(Patterns);
#     Patterns = Loadpickle(os.path.join(pkdir,'Patterns.pk'));
#     mtRegExplst = Loadpickle(os.path.join(pkdir,'mtRegExpList.pk'));
    #emptyTree = Tree('ROOT',[])
#     ShowPatterns(Patterns)
#     #print mtRegExplst[29].pattern
    #CEcases = GettingCEcases([pattern(0,0,[0,0,0],'&R@Complete@','')], [re.compile(ur'(.*)')], emptyTree, Tree('S',[Tree('VB',['is'])]), emptyTree);
#     for ce in CEcases:
#         ShowCELink(ce); 