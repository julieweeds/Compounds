__author__ = 'juliewe'

def configure(args):
    parameters={}
    parameters['testing']=False
    parameters['source']='trial'
    parameters['parentdir']='~/'
    parameters['datadir']='Documents/workspace/Compounds/data/lexsub/'+parameters['source']
    parameters['basename']='lexsub_'+parameters['source']
    parameters['datafile']=parameters['basename']+'.fixed.xml'


    for arg in args:
        if arg == 'testing':
            parameters['testing']=True
        if arg == 'local':
            parameters['parentdir']='/Volumes/LocalScratchHD/juliewe/'
        elif arg == 'athome':
            parameters['parentdir']='/Users/juliewe/'

    parameters['datadir']=parameters['parentdir']+parameters['datadir']

    return parameters
