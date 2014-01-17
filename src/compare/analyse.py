__author__ = 'juliewe'

import conf,sys,os
import numpy as np


if __name__=='__main__':

    parameters=conf.configure(sys.argv)
    filename='stats.diff.csv'

    filepath=os.path.join(parameters['datadir'],filename)
    print "Processing "+filepath


    metrics=['PPMI']
    phrases=[]
    lines=[]
    with open(filepath,'r') as instream:
        for line in instream:
            lines.append(line.rstrip())

    #process line0

    fields=lines[0].split(',')
    metrics=metrics+list(fields[:-1])
    #print len(metrics),metrics

    #process line 1
    #print lines[1]
    phrases=list(lines[1].split(',')[:-1])

    #process rest
    scores={}
    for i,metric in enumerate(metrics):
        scores[metric]=[]
        lineno=i+2
        #print metric
        fields=lines[lineno].split(',')
        #print fields
        scores[metric] = list(fields[:-1])

    #make list of adjectives
    adjectives={}
    for index,phrase in enumerate(phrases):
        parts=phrase.split(':')
        #print parts
        tag = parts[2].split('/')[1]
        if tag == 'J':
            adjectives[parts[2]]=adjectives.get(parts[2],0)+index

    print len(adjectives.keys()),adjectives.keys()
    print adjectives.values()

    outpath=os.path.join(parameters['datadir'],'adjanal.csv')
    outstream = open(outpath,'w')
    output=''
    for metric in metrics:
        output=output+','+metric
    output+='\n'
    outstream.write(output)
    for adj in adjectives:
        adjscores={}
        for metric in metrics:
            adjscores[metric]=[]
        totalindex=0
        for index,phrase in enumerate(phrases):
            parts=phrase.split(':')
            if parts[2]==adj:
                for metric in metrics:
                    adjscores[metric].append(float(scores[metric][index]))
                totalindex+=index
        means={}
        sds={}
        output=adj
        for metric in metrics:
            scorearray=np.array(adjscores[metric])
            means[metric]=np.mean(scorearray)
            sds[metric]=np.std(scorearray)
            output=output+','+str(means[metric])

        print adj
        print means
        print sds
        outstream.write(output+'\n')

    outstream.close()