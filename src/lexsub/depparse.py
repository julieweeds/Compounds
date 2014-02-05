__author__ = 'juliewe'
import sys,os
from conf import configure
import nltk.parse.malt as malt

if __name__=='__main__':
    parameters=configure(sys.argv)
    sentencefile=parameters['datafile']+'.sents'
    sentencepath=os.path.join(parameters['datadir'],sentencefile)
    print sentencepath

    with open(sentencepath,'r') as sentencestream:
        lineno=0
        for line in sentencestream:
            lineno+=1
            print lineno, line.rstrip()

            myparser=malt.MaltParser()
            myparser.config_malt(bin='/Volumes/LocalScratchHD/juliewe/maltparser-1.7.2/maltparser-1.7.2.jar')
            myparser.train([])
            myparser.parse(line)
            exit()