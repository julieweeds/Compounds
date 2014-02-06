__author__ = 'juliewe'
def configure(args):

    parameters={}
    parameters['parentdir']=''
    parameters['datadir']='juliewe/Documents/workspace/Compounds/data/ijcnlp_compositionality_data'
    parameters['datafile']='MeanAndDeviations.clean.txt'
    parameters['athome']=False
    parameters['local']=True


    for arg in args:
        if arg=='testing':
            parameters['testing']=True
        elif arg=='local':
            parameters['local']=True
            parameters['athome']=False
        elif arg=='athome':
            parameters['athome']=True
            parameters['local']=False

    if parameters['local']:
        parameters['parentdir']='/Volumes/LocalScratchHD/'

    return parameters