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
    parameters['ks']=[0,1,2,5,10,20,30,50,75,100]
    #parameters['ks']=[0,1,5]
    parameters['k']=5
    parameters['freqdiff']=False
    parameters['usefreqthresh']='none'
    parameters['freqthresh']=0
    parameters['neighsource']=''

    parameters['typelist']=['phrase','head','mod']
    #parameters['typelist']=['phrase']


    for i,arg in enumerate(args):
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
        elif arg=='comp_min':
            parameters['neighsource']='comp_min'
        elif arg=='comp_nfmult':
            parameters['neighsource']='comp_nfmult'
        elif arg=='diffcomp_min':
            parameters['neighsource']='diffcomp_min'
        elif arg=='diffcomp_mult':
            parameters['neighsource']='diffcomp_mult'
        elif arg=='diffcomp_gm':
            parameters['neighsource']='diffcomp_gm'
        elif arg=='diffcomp_nfgm':
            parameters['neighsource']='diffcomp_nfgm'
        elif arg=='diffcomp_nfmult':
            parameters['neighsource']='diffcomp_nfmult'
        elif arg=='unigram':
            parameters['neighsource']='unigram'
            parameters['typelist']=['head','mod']
        elif arg=='setk':
            parameters['ks']=[int(args[i+1])]
        elif arg=='freqdiff':
            parameters['freqdiff']=True
        elif arg=='abovefreqthresh':
            parameters['usefreqthresh']='above'
            parameters['freqthresh']=500

        elif arg=='belowfreqthresh':
            parameters['usefreqthresh']='below'
            parameters['freqthresh']=500

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
    parameters['freqfile']='vectors.train.PHRASES.entries.strings'
    parameters['pseudofile']='pseudopairs.nf2'

    return parameters
