__author__ = 'juliewe'

def configure(args):

    parameters={}
    parameters['pos']='N'
    parameters['testing']=False

    parameters['filenames']={'N':'wikiPOS_nounsdeps_t100.pbfiltered','J':'wikiPOS_adjsdeps_t100.pbfiltered'}
    parameters['seed']=37
    parameters['ratio']=0.8
    parameters['local']=False
    parameters['apollo']=False
    parameters['athome']=True
    parameters['vectorfiles']={'train':'vectors.train.PHRASES','test':'vectors.test.PHRASES','constituents':'vectors.train.CONSTITUENTS'}
    parameters['deps']=['nn-DEP']
    parameters['filter']=False
    parameters['setup']=False

    for arg in args:
        if arg=='nouns' or arg=='N':
            parameters['pos']='N'
        elif arg=='adjs' or arg=='J':
            parameters['pos']='J'
        elif arg=='testing':
            parameters['testing']=True
        elif arg=='filter':
            parameters['filter']=True
        elif arg=='setup':
            parameters['setup']=True
            parameters['deps'].append('word')

    parameters=setfilenames(parameters)
    return parameters

def setfilenames(parameters):

    if parameters['apollo']:
        parameters['datadir']='/mnt/lustre/scratch/inf/juliewe/FeatureExtractionToolkit/feoutput-deppars'
        parameters['compoundparentdir']='/mnt/lustre/scratch/inf/juliewe/Compounds/data/'

    if parameters['local']:
        parameters['compoundparentdir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds/data/'

    if parameters['athome']:
        parameters['compoundparentdir']='/Users/juliewe/Documents/workspace/Compounds/data/'

    parameters['compdatadir']=parameters['compoundparentdir']+'ijcnlp_compositionality_data/NNs/nouns/'

    return parameters
