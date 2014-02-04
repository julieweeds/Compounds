__author__ = 'juliewe'

def configure(args):

    parameters={}
    parameters['pos']='N'
    parameters['testing']=False
    parameters['datadir']='/mnt/lustre/scratch/inf/juliewe/FeatureExtractionToolkit/feoutput-deppars'
    parameters['filenames']={'N':'wikiPOS_nounsdeps_t100.pbfiltered','J':'wikiPOS_adjsdeps_t100.pbfiltered'}
    parameters['seed']=37
    parameters['ratio']=0.8

    for arg in args:
        if arg=='nouns' or arg=='N':
            parameters['pos']='N'
        elif arg=='adjs' or arg=='J':
            parameters['pos']='J'
        elif arg=='testing:':
            parameters['testing']=True
    return parameters