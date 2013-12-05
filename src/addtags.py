__author__ = 'juliewe'

import sys,os
from conf import configure

tagdict={}
tagdict['N']={'amod-DEP':'J','dobj-HEAD':'V','conj-DEP':'N','nsubj-HEAD':'V','pobj-HEAD':'V'}
tagdict['J']={'amod-HEAD':'N','amod-DEP':'J','conj-DEP':'J'}

if __name__=="__main__":

    parameters=configure(sys.argv)
    filepath = os.path.join(parameters['parentdir'],parameters['altdatadir'],sys.argv[1])
    print "Adding tags to "+filepath
    outpath=filepath+".tagged"

    with open(filepath,'r') as instream:
        with open(outpath,'w') as outstream:

            linesread=0
            for line in instream:
                fields=line.rstrip().split('\t')

                for i,field in enumerate(fields):
                    parts=field.split(':')
                    if i==0:
                        try:
                            linetag=parts[0].split('/')[1]
                        except IndexError:
                            linetag=parameters['tag']
                    if i==0 or parameters['tagall']:
                        if len(parts)>1:
                            feature=parts[-2]
                            tag=tagdict[linetag].get(feature,linetag)
                            field=field+'/'+tag
                    if i>0:
                        outstream.write('\t')
                    outstream.write(field)
                outstream.write('\n')
                linesread+=1
                if linesread%10000==0:print "Processed "+str(linesread)+" lines"
