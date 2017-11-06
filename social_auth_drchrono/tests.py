# -*- coding:utf-8 -*-

import sys
import urllib
import urlparse
import re
from hmmlearn import hmm
import numpy as np
from sklearn.externals import joblib
import HTMLParser
import nltk


MIN_LEN=10
N=5
T=-200
SEN=['<','>',',',':','\'','/',';','"','{','}','(',')']

index_wordbag=1
wordbag={}
tokens_pattern = r'''(?x)
 "[^"]+"
|http://\S+
|</\w+>
|<\w+>
|<\w+
|\w+=
|>
|\w+\([^<]+\) #函数 比如alert(String.fromCharCode(88,83,83))
|\w+
'''

def ischeck(str):
    if re.match(r'^(http)',str):
        return False
    for i, c in enumerate(str):
        if ord(c) > 127 or ord(c) < 31:
            return False
        if c in SEN:
            return True


    return False


def do_str(line):
    words=nltk.regexp_tokenize(line, tokens_pattern)
    return words

def load_wordbag(filename,max=100):
    X = [[0]]
    X_lens = [1]
    tokens_list=[]
    global wordbag
    global index_wordbag

    with open(filename) as f:
        for line in f:
            line=line.strip('\n')
            line=urllib.unquote(line)
            h = HTMLParser.HTMLParser()
            line=h.unescape(line)
            if len(line) >= MIN_LEN:
                line, number = re.subn(r'\d+', "8", line)
                line, number = re.subn(r'(http|https)://[a-zA-Z0-9\.@&/#!#\?:=]+', "http://u", line)
                line, number = re.subn(r'\/\*.?\*\/', "", line)
                tokens_list+=do_str(line)

    fredist = nltk.FreqDist(tokens_list)
    keys=fredist.keys()
    keys=keys[:max]
    for localkey in keys:
        if localkey in wordbag.keys():
            continue
        else:
            wordbag[localkey] = index_wordbag
            index_wordbag += 1

    print "GET wordbag size(%d)" % index_wordbag
def main(filename):
    X = [[-1]]
    X_lens = [1]
    global wordbag
    global index_wordbag

    with open(filename) as f:
        for line in f:
            line=line.strip('\n')
            line=urllib.unquote(line)
            h = HTMLParser.HTMLParser()
            line=h.unescape(line)
            if len(line) >= MIN_LEN:
                line, number = re.subn(r'\d+', "8", line)
                line, number = re.subn(r'(http|https)://[a-zA-Z0-9\.@&/#!#\?:]+', "http://u", line)
                line, number = re.subn(r'\/\*.?\*\/', "", line)
                words=do_str(line)
                vers=[]
                for word in words:
                    if word in wordbag.keys():
                        vers.append([wordbag[word]])
                    else:
                        vers.append([-1])

            np_vers = np.array(vers)
            X=np.concatenate([X,np_vers])
            X_lens.append(len(np_vers))


    remodel = hmm.GaussianHMM(n_components=N, covariance_type="full", n_iter=100)
    remodel.fit(X,X_lens)
    joblib.dump(remodel, "xss-train.pkl")

    return remodel

def test(remodel,filename):
    with open(filename) as f:
        for line in f:
            line = line.strip('\n')
            line = urllib.unquote(line)
            h = HTMLParser.HTMLParser()
            line = h.unescape(line)

            if len(line) >= MIN_LEN:
                line, number = re.subn(r'\d+', "8", line)
                line, number = re.subn(r'(http|https)://[a-zA-Z0-9\.@&/#!#\?:]+', "http://u", line)
                line, number = re.subn(r'\/\*.?\*\/', "", line)
                words = do_str(line)
                vers = []
                for word in words:
                    if word in wordbag.keys():
                        vers.append([wordbag[word]])
                    else:
                        vers.append([-1])

                np_vers = np.array(vers)
                pro = remodel.score(np_vers)

                if pro >= T:
                    print  "SCORE:(%d) XSS_URL:(%s) " % (pro,line)

def test_normal(remodel,filename):
    with open(filename) as f:
        for line in f:
            result = urlparse.urlparse(line)
            query = urllib.unquote(result.query)
            params = urlparse.parse_qsl(query, True)

            for k, v in params:
                v=v.strip('\n')

                if len(v) >= MIN_LEN:
                    v, number = re.subn(r'\d+', "8", v)
                    v, number = re.subn(r'(http|https)://[a-zA-Z0-9\.@&/#!#\?:]+', "http://u", v)
                    v, number = re.subn(r'\/\*.?\*\/', "", v)
                    words = do_str(v)
                    vers = []
                    for word in words:
                        if word in wordbag.keys():
                            vers.append([wordbag[word]])
                        else:
                            vers.append([-1])

                    np_vers = np.array(vers)
                    pro = remodel.score(np_vers)
                    print  "CHK SCORE:(%d) QUREY_PARAM:(%s)" % (pro, v)
if __name__ == '__main__':
    load_wordbag(sys.argv[1],2000)
    remodel = main(sys.argv[1])
    test(remodel, sys.argv[2])

