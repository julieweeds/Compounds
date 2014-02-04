__author__ = 'juliewe'

#split output of feature extractor into training and test data
#this means context for one constituent could be in training and for the other could be in the test.
#would it be better to use sequential selection?
#or is this what we want?  Randomly remove 20% of the data and see if we can reconstruct it through composition and nearest neighbours?

import os,sys,random
from conf import configure

if __name__=='__main__':

    parameters= configure(sys.argv)
    print parameters
    filename=parameters['filenames'][parameters['pos']]
    filepath=os.path.join(parameters['datadir'],filename)
    print "File to be processed is: "+filepath
    trainpath=filepath+'.train'
    testpath=filepath+'.test'

    random.seed(parameters['seed'])
    with open(filepath,'r') as instream:
        with open(trainpath,'w') as trainstream:
            with open(testpath,'w') as teststream:
                for line in instream:
                    r = random.randint(1,100)

                    if r>float(parameters['ratio'])*100:
                        teststream.write(line)
                    else:
                        trainstream.write(line)

