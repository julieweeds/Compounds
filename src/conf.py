__author__ = 'juliewe'

def configure(args):

    parameters={}
    parameters['parentdir']='/Volumes/LocalScratchHD/juliewe/Documents/workspace/Compounds'

    parameters['datadir']='data/Wiki_nounsdeps'
    parameters['freqfile']='events.strings'
    parameters['assocfile']='events.strings_mi'
    parameters['entryfile']='events.strings_deprow'
    parameters['featurefile']='events.strings_depcol'
    parameters['freqthresh']=100
    parameters['sample']=1500
    parameters['entrythresh']=10000
    parameters['stopwordlimit']=3
    parameters['featurematch']='nn-DEP'
    parameters['tagmatch']='N'
    parameters['inversefeatures']={'nn-DEP':'nn-HEAD','nn-HEAD':'nn-DEP','amod-DEP':'amod-HEAD','amod-HEAD':'amod-DEP'}
    parameters['testing']=False
    parameters['deplist']=['amod-DEP','dobj-HEAD','conj-DEP','iobj-HEAD','nsubj-HEAD','nn-DEP','nn-HEAD','pobj-HEAD','amod-HEAD']

    parameters['collocatefile']='multiwords_'+parameters['featurematch']
    parameters['depfile']='wikipedia_nounsdeps_t100.pbfiltered'
    parameters['extract']=False
    parameters['build']=False
    parameters['usesource']=False
    parameters['source']='none'
    parameters['allheads']=False
    parameters['adjlist']=False
    parameters['usefile']='train'
    parameters['windows']=False
    #parameters['raw']=False
    parameters['phrasetype']='ANs'
    parameters['posdict']={'N':'nouns','J':'adjs','R':'advs','V':'verbs'}
    for arg in args:
        if arg=='testing':
            parameters['testing']=True
        elif arg=='apollo':
            parameters['parentdir']='/mnt/lustre/scratch/inf/juliewe/Compounds'
        elif arg =='extract':
            parameters['extract']=True
        elif arg =='build':
            parameters['build']=True
        elif arg=='raw':
            parameters['raw']=True  #leave vectors in raw frequency form rather than converting to PPMI
        elif arg =='boleda':
            parameters['usesource']=True
            parameters['source']='boleda.txt'
            parameters['datadir']='data/ANcompounds'
            parameters['featurematch']='amod-DEP'
            parameters['freqthresh']=0
            parameters['mergefile']='multiwords_boleda'
            parameters['collocatefile']='multiwords_amod-DEP_boleda'

        elif arg =='Jboleda':
            parameters['usesource']=True
            parameters['source']='boleda.txt'
            parameters['datadir']='data/ANcompounds/deps/adjs'
            parameters['featurematch']='amod-HEAD'
            parameters['freqthresh']=0
            parameters['mergefile']='multiwords_boleda'
            parameters['collocatefile']='multiwords_amod-HEAD_boleda'
            parameters['allheads']=True

        elif arg == 'Jextract':
            parameters['datadir']='data/ANcompounds/deps/adjs'
            parameters['featurematch']='amod-HEAD'
            parameters['freqthresh']=100
            parameters['upperfreqthresh']=100
            parameters['collocatefile']='multiwords_amod-HEAD'
            parameters['allheads']=True
        elif arg=='train':
            parameters['usefile']='train'
        elif arg=='test':
            parameters['usefile']='test'
        elif arg=='Jwin':
            parameters['windows']=True
            parameters['usesource']=True
            parameters['source']='adjs32'
            #            parameters['usefile']='train'
            parameters['datadir']='data/ANcompounds/wins/adjs'
            parameters['altdatadir']='data/ANcompounds/wins/nouns'
            parameters['altdepfile']='wikipedia_nounsdeps_t100.pbfiltered'
            #parameters['depfile']='wikipedia_adjsdeps_t100.pbfiltered.'+parameters['usefile']
            parameters['depfile']='wikipedia_AN_t100.pbfiltered'
            parameters['deplist']='T'
            parameters['featurefile']='events.strings_domcol'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords.train','multiwords.test','multiwords.spare']
            parameters['freqthresh']=100
            parameters['featurematch']='amod-HEAD'
            parameters['nfmod']=True

        elif arg =='Jlist':
            parameters['usesource']=True
            parameters['source']='adjs32'
#            parameters['usefile']='train'
            parameters['datadir']='data/ANcompounds/deps/adjs'
            parameters['altdatadir']='data/ANcompounds/deps/nouns'
            parameters['altdepfile']='wikiPOS_nounsdeps_t100.pbfiltered'
            parameters['depfile']='wikiPOS_adjsdeps_t100.pbfiltered.'+parameters['usefile']
            parameters['featurefile']='features.strings'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords.train','multiwords.test','multiwords.spare']
            parameters['freqthresh']=100
            parameters['featurematch']='amod-HEAD'
            parameters['tagmatch']='N'
            parameters['tagall']=False
            parameters['tag']=parameters['tagmatch'] #tag obsolete i think
            #parameters['nfmod']=True
            #parameters['domods']=True
        elif arg =='NFmod':
            parameters['nfmod']=True
        elif arg=='ANs':
            parameters['phrasetype']='ANs'
            parameters['lefttype']='J'
            parameters['righttype']='N'
        elif arg=='NNs':
            parameters['phrasetype']='NNs'
            parameters['lefttype']='N'
            parameters['righttype']='N'

        elif arg=='miro':
            parameters['datadir']='data/miro/'+parameters['phrasetype']+'/'+parameters['posdict'][parameters['lefttype']]
            parameters['altdatadir']='data/miro/'+parameters['phrasetype']+'/'+parameters['posdict'][parameters['righttype']]
            parameters['depfile']='exp10'
            parameters['altdepfile']='exp10'
            parameters['featurefile']='features.strings'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords']
            parameters['usefile']='all'
            if parameters['phrasetype']=='ANs':
                parameters['featurematch']='amod-HEAD'
            elif parameters['phrasetype']=='NNs':
                parameters['featurematch']='nn-DEP'
            parameters['deplist']=['advmod-HEAD','advmod-DEP','amod-DEP','amod-HEAD','conj-DEP','conj-HEAD','dobj-DEP','dobj-HEAD','iobj-DEP','iobj-HEAD','nn-DEP','nn-HEAD','nsubj-HEAD','nsubj-DEP','pobj-HEAD']
    return parameters
