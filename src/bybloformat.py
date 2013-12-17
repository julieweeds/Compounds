__author__ = 'juliewe'
#code to reformat generated files into byblo format (with correct pos at end of entry) and calculate entry totals

#good/J:amod-HEAD:doctor/N needs to be compared with adjectives so better format is
#--> good[amod-HEAD:doctor/N]/J

import sys,os

def findtotal(featurelist):
    total=0
    while len(featurelist)>0:
        score=float(featurelist.pop())
        f=featurelist.pop()
        total+=score

    return total
if __name__=="__main__":

    datadir="/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/ANcompounds/deps/adjs"
    if len(sys.argv)>1:
        filename=sys.argv[1]
    datapath=os.path.join(datadir,filename)

    if len(sys.argv)>2:
        required_tag=sys.argv[2]
    else:
        required_tag='J'

    eventpath=datapath+".events.strings"
    entrypath=datapath+".entries.strings"


    with open(datapath,'r') as instream:
        with open(eventpath,'w') as eventstream:
            with open(entrypath,'w') as entrystream:
                print "Processing "+datapath
                linesread=0
                for line in instream:
                    linesread+=1
                    if linesread%100==0:
                        print"Processed "+str(linesread)+" lines"
                        #exit()
                    fields=line.rstrip().split('\t')
                    total=findtotal(fields[1:])
                    parts=fields[0].split(':')
                    if len(parts)==3:
                        (word,tag)=parts[0].split('/')
                        fields[0]=word+'['+parts[1]+':'+parts[2]+']/'+tag

                    else:
                        parts=fields[0].split('@')
                        if len(parts)==3:
                            (word,tag)=parts[0].split('/')
                            fields[0]=word+'[@'+parts[1]+'@'+parts[2]+']/'+tag
                        else:
                            print "Incorrect format of phrase "+fields[0]
                            exit(1)
                    if total>0 and tag==required_tag:
                        entrystream.write(fields[0]+'\t'+str(total)+'\n')
                        eventstream.write('\t'.join(fields)+'\n')
                    else:
                        print "Ignoring zero vector for "+fields[0]