__author__ = 'juliewe'

import numpy as np

datadir='/Users/juliewe/Dropbox/coling14/stats/'
prefix='stats.diff.train.'
infix='gm.funct'
suffix='.pmi.compsecond.pmi.csv'
filename=datadir+prefix+infix+suffix

rel='nn-DEP'
ut=3
lt=2



if __name__=='__main__':

    with open(filename,'r') as instream:

        linesread=0
        for line in instream:

            linesread+=1
            if linesread==2:
                phrases=line.rstrip().split(',')
            elif linesread==3:
                compscorelist=line.rstrip().split(',')
            elif linesread==6:
                cosscorelist=line.rstrip().split(',')


    highscores=[]
    lowscores=[]

    print phrases
    print compscorelist
    print cosscorelist

    for (phrase,comp,cos) in zip(phrases,compscorelist,cosscorelist):
        parts=phrase.split(':')
        if len(parts)==3:
            if parts[1]==rel:
                if float(comp)>=ut:
                    highscores.append(float(cos))
                elif float(comp)<lt:
                    lowscores.append(float(cos))

    print highscores
    print lowscores

    higharray=np.array(highscores)
    lowarray=np.array(lowscores)

    highmean=np.average(highscores)
    lowmean=np.average(lowscores)
    highstd=np.std(highscores)
    lowstd=np.std(lowscores)

    print infix
    print "High: ",str(highmean),str(highstd)
    print "Low: ",str(lowmean),str(lowstd)

