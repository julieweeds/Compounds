__author__ = 'juliewe'

def configure(args):

    parameters={}
    parameters['pos']='N'
    parameters['testing']=False

    parameters['filenames']={'N':'wikiPOS_nounsdeps_t100.pbfiltered','J':'wikiPOS_adjsdeps_t100.pbfiltered'}
    parameters['seed']=37
    parameters['ratio']=0.8
    parameters['local']=True
    parameters['apollo']=False
    parameters['athome']=False
    parameters['vectorfiles']={'train':'vectors.train.PHRASES','test':'vectors.test.PHRASES','constituents':'vectors.train.CONSTITUENTS','nouns':'vectors.train.ALLNOUNS'}
    parameters['deps']=['nn-DEP']
    parameters['filter']=False
    parameters['setup']=False
    parameters['run_neighs']=False
    parameters['run_vectors']=False
    parameters['k']=30
    parameters['typelist']=['phrase','head']
    #parameters['typelist']=['phrase']

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
        elif arg=='local':
            parameters['local']=True
            parameters['apollo']=False
            parameters['athome']=False
        elif arg=='athome':
            parameters['athome']=True
            parameters['local']=False
            parameters['apollo']=False
        elif arg=='apollo':
            parameters['apollo']=True
            parameters['local']=False
            parameters['athome']=False
        elif arg=='neighs' or arg=='run_neighs':
            parameters['run_neighs']=True
        elif arg=='vectors' or arg == 'run_vectors':
            parameters['run_vectors']=True
        elif arg=='obs' or arg =='observed':
            parameters['neighsource']='observed'
        elif arg=='comp_mult':
            parameters['neighsource']='comp_mult'
        elif arg=='comp_gm':
            parameters['neighsource']='comp_gm'

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
    parameters['neighfile']=parameters['neighsource']+'.neighbours.strings'
    parameters['phrasefile']=parameters['neighsource']+'.vectors.train.PHRASES'
    parameters['constitfile']=parameters['vectorfiles']['nouns']
    parameters['pseudofile']='pseudopairs'

    return parameters
