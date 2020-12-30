# Cause-Effect Extraction System

## Overview

In this folder, we have our cause-effect extraction system based on Cao et al. The original repo can be found [here](https://github.com/Angela7126/CE_extractor--Patterns_Based). We have modified the repo to include only the necessary code for our pipeline and also provide scripts to parse the TQA and SQuAD 2.0-dev datasets.

## Setup and Installation

The repo is written in python2, so you should create a separate environment to run code for this part of the pipeline. If you want some guidance to download and install python2 and setup a virtual environment, we recommend the following guides.

- [Installation](https://help.dreamhost.com/hc/en-us/articles/115000218612-Installing-a-custom-version-of-Python-2)
- [Virtual Environment](https://help.dreamhost.com/hc/en-us/articles/215489338-Installing-and-using-virtualenv-with-Python-2)

You will also need to download [stanford-corenlp-full-2015-04-20](http://nlp.stanford.edu/software/stanford-corenlp-full-2015-04-20.zip) and [stanford-parse-full-2015-04-20](https://nlp.stanford.edu/software/stanford-parser-full-2015-04-20.zip) in order to run the parser. The code assumes the jar files from these are located in same location as this directory, so if you download them into a different directroy you will need to change the following lines (37-38) in `cmyPatternMatching.py`:

```python
os.environ['STANFORD_PARSER'] = r'../../stanford-parser.jar'
os.environ['STANFORD_MODELS'] = r'../../stanford-parser-3.5.2-models.jar'
```

Additionaly, the code also needs the `englishPCFG.ser.gz`. This can be obtained by following the steps in this SO [post](https://stackoverflow.com/questions/40820140/how-to-get-englishpcfg-ser-gz-as-a-single-file).

Since the parser is written in Java, you will also need JDK1.8.0.

## Datasets

We ran our experiments using the Textbook Question Answering (TQA) and SQuAD 2.0 development datasets. You can run the provided `get_tqa` script to download the TQA dataset and you can download the SQuAD data [here](https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json).

Let us know if you have any questions!
