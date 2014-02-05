__author__ = 'juliewe'

def configure(args):
    parameters={}
    parameters['testing']=False
    parameters['datadir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/lexsub/trial'
    parameters['datafile']='lexsub_trial.fixed.xml'


    for arg in args:
        if arg == 'testing':
            parameters['testing']=True

    return parameters
