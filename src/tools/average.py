__author__ = 'juliewe'

import sys,numpy as np

if __name__=='__main__':

    filename=sys.argv[1]
    print filename

    values=[]
    with open(filename,'r') as instream:
        for line in instream:
            fields=line.rstrip().split('\t')
            values.append(float(fields[1]))

    myarray=np.array(values)

    mean=np.average(myarray)
    median=np.percentile(myarray,50)
    print mean,median
