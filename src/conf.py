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
    parameters['phrasefeatures']={'ANs':'amod-HEAD','NNs':'nn-HEAD'}  #this is the dep in the file for the left pos NOT the dep in the multiwords file (this can be either the same or the inverse)
    parameters['testing']=False
    parameters['deplist']=['amod-DEP','dobj-HEAD','conj-DEP','conj-HEAD','iobj-HEAD','nsubj-HEAD','nn-DEP','nn-HEAD','amod-HEAD','advmod-HEAD','advmod-DEP']

    parameters['collocatefile']='multiwords_'+parameters['featurematch']
    parameters['depfile']='wikipedia_nounsdeps_t100.pbfiltered'
    parameters['extract']=False
    parameters['build']=False
    parameters['make_entries']=False
    parameters['usesource']=False
    parameters['source']='none'
    parameters['allheads']=False
    parameters['adjlist']=False
    parameters['usefile']='train'
    parameters['windows']=False
    #parameters['raw']=False
    parameters['phrasetype']='ANs'
    parameters['lefttype']='J'
    parameters['righttype']='N'
    parameters['posdict']={'N':'nouns','J':'adjs','R':'advs','V':'verbs'}
    parameters['vsource']='giga'
    parameters['msource']='r8'
    parameters['miroflag']=False
    parameters['NNcompflag']=False
    parameters['wins']=False

    for arg in args:
        if arg=='testing':
            parameters['testing']=True
        elif arg=='apollo':
            parameters['parentdir']='/mnt/lustre/scratch/inf/juliewe/Compounds'
        elif arg =='extract':
            parameters['extract']=True
        elif arg =='build':
            parameters['build']=True
        elif arg=='make_entries':
            parameters['make_entries']=True
        elif arg=='raw':
            parameters['raw']=True  #leave vectors in raw frequency form rather than converting to PPMI

        elif arg=='train':
            parameters['vsource']='train'
        elif arg=='test':
            parameters['vsource']='test'
        elif arg == 'NNcomp':
            parameters['NNcompflag']=True
            parameters['phrasetype']='NNs'
            parameters['lefttype']='N'
            parameters['righttype']='N'

            parentdir='data/ijcnlp_compositionality_data/'
            parameters['datadir']=parentdir+parameters['phrasetype']+'/'+parameters['posdict'][parameters['lefttype']]
            parameters['altdatadir']=parentdir+parameters['phrasetype']+'/'+parameters['posdict'][parameters['righttype']]
            parameters['depfile']='wikiPOS.'+parameters['vsource']
            parameters['altdepfile']=parameters['depfile']
            parameters['featurefile']=parameters['depfile']+'.features.strings'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords']
            parameters['usefile']='all'
            parameters['featurematch']='nn-HEAD'
            parameters['deplist']=['advmod-HEAD','advmod-DEP','amod-DEP','amod-HEAD','conj-DEP','conj-HEAD','dobj-DEP','dobj-HEAD','iobj-DEP','iobj-HEAD','nn-DEP','nn-HEAD','nsubj-HEAD','nsubj-DEP','pobj-HEAD']
        elif arg =='boleda':
            parameters['usesource']=True
            parameters['source']='boleda.txt'
            parameters['datadir']='data/ANcompounds'
            parameters['featurematch']='amod-HEAD'
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
        elif arg=='wins':
            parameters['wins']=True
        elif arg=='giga':
            parameters['vsource']='giga'
        elif arg=='wiki':
            parameters['vsource']='wiki'
        elif arg=='movies':
            parameters['msource']='movies'
        elif arg=='r8':
            parameters['msource']='r8'
        elif arg=='miro':
            parentdir='data/miro/'
            if parameters['msource']=='movies':
                parentdir=parentdir+'movies/'
            parameters['datadir']=parentdir+parameters['phrasetype']+'/'+parameters['posdict'][parameters['lefttype']]
            parameters['altdatadir']=parentdir+parameters['phrasetype']+'/'+parameters['posdict'][parameters['righttype']]
            if parameters['vsource']=='giga':
                parameters['depfile']='exp10'
                parameters['altdepfile']='exp10'
            elif parameters['vsource']=='wiki':
                parameters['depfile']='wikiPOS'
                parameters['altdepfile']='wikiPOS'
            parameters['featurefile']=parameters['depfile']+'.features.strings'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords']
            parameters['usefile']='all'
            if parameters['phrasetype']=='ANs':
                parameters['featurematch']='amod-HEAD'
            elif parameters['phrasetype']=='NNs':
                parameters['featurematch']='nn-DEP'
            parameters['deplist']=['advmod-HEAD','advmod-DEP','amod-DEP','amod-HEAD','conj-DEP','conj-HEAD','dobj-DEP','dobj-HEAD','iobj-DEP','iobj-HEAD','nn-DEP','nn-HEAD','nsubj-HEAD','nsubj-DEP','pobj-HEAD']
        elif arg=='miro_feb':
            parentdir='data/miro0214/giga_wiki_NPs_in_MR_R2_frequent.uniq.50/'
            parameters['datadir']=parentdir+parameters['vsource']+'/'+parameters['phrasetype']+'/'+parameters['posdict'][parameters['lefttype']]
            parameters['altdatadir']=parentdir+parameters['vsource']+'/'+parameters['phrasetype']+'/'+parameters['posdict'][parameters['righttype']]
            if parameters['vsource']=='giga':
                parameters['depfile']='exp10'
                parameters['altdepfile']='exp10'
            elif parameters['vsource']=='wiki':
                parameters['depfile']='wikiPOS'
                parameters['altdepfile']='wikiPOS'
            parameters['featurefile']=parameters['depfile']+'.features.strings'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords']
            parameters['miroflag']=True
            parameters['usefile']='all'
            if parameters['phrasetype']=='ANs':
                parameters['featurematch']='amod-HEAD'
            elif parameters['phrasetype']=='NNs':
                parameters['featurematch']='nn-HEAD'
            parameters['deplist']=['advmod-HEAD','advmod-DEP','amod-DEP','amod-HEAD','conj-DEP','conj-HEAD','dobj-DEP','dobj-HEAD','iobj-DEP','iobj-HEAD','nn-DEP','nn-HEAD','nsubj-HEAD','nsubj-DEP','pobj-HEAD']
        elif arg=='miro_mar':
            parentdir='data/miro0314/'
            parameters['datadir']=parentdir+parameters['phrasetype']+'/'+parameters['posdict'][parameters['lefttype']]
            parameters['altdatadir']=parentdir+parameters['phrasetype']+'/'+parameters['posdict'][parameters['righttype']]
            if parameters['vsource']=='giga':
                parameters['depfile']='exp10'
                parameters['altdepfile']='exp10'
            elif parameters['vsource']=='wiki':
                parameters['depfile']='wikiPOS'
                parameters['altdepfile']='wikiPOS'
            parameters['featurefile']=parameters['depfile']+'.features.filtered.strings'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords']
            parameters['miroflag']=False
            parameters['usefile']='all'
            if parameters['phrasetype']=='ANs':
                parameters['featurematch']='amod-HEAD'
            elif parameters['phrasetype']=='NNs':
                parameters['featurematch']='nn-HEAD'
            parameters['deplist']=['advmod-HEAD','advmod-DEP','amod-DEP','amod-HEAD','conj-DEP','conj-HEAD','dobj-DEP','dobj-HEAD','iobj-DEP','iobj-HEAD','nn-DEP','nn-HEAD','nsubj-HEAD','nsubj-DEP','pobj-HEAD']

        elif arg=='wn_wiki':
            #phrasetype should be set first via ANs or NNs
            #wins should be set first
            if parameters['phrasetype']=='ANs':
                parameters['featurematch']='amod-HEAD'
            else:
                parameters['featurematch']=='nn-HEAD'

            if parameters['wins']:
                parameters['deplist']=['T']
                parameters['depfile']='wikiPOS_'+parameters['posdict'][parameters['lefttype']]
                parameters['altdepfile']='wikiPOS_'+parameters['posdict'][parameters['righttype']]
                parameters['featurefile']=parameters['depfile']+'wins.features.strings'
                parameters['vinfix']='wins'
            else:
                parameters['depfile']='wikiPOS_'+parameters['posdict'][parameters['lefttype']]+'deps'
                parameters['altdepfile']='wikiPOS_'+parameters['posdict'][parameters['righttype']]+'deps'
                parameters['featurefile']=parameters['depfile']+'.features.strings'
                parameters['vinfix']='deps'
                parameters['deplist']=['advmod-HEAD','advmod-DEP','amod-DEP','amod-HEAD','conj-DEP','conj-HEAD','dobj-DEP','dobj-HEAD','iobj-DEP','iobj-HEAD','nn-DEP','nn-HEAD','nsubj-HEAD','nsubj-DEP','pobj-HEAD']

            parameters['altfeaturefile']=parameters['altdepfile']+'.features.strings'
            parentdir='data/WNcompounds/'
            parameters['datadir']=parentdir+parameters['vinfix']+'/'+parameters['phrasetype']+'/'+parameters['posdict'][parameters['lefttype']]
            parameters['altdatadir']=parentdir+parameters['vinfix']+'/'+parameters['phrasetype']+'/'+parameters['posdict'][parameters['righttype']]

            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords.wn_wiki']
            parameters['usefile']=parameters['phrasetype']
            parameters['miroflag']=False
            parameters['featurematch']=parameters['phrasefeatures'][parameters['phrasetype']]
            parameters['funct']=True
            parameters['diff']=True
            parameters['compop']='gm'
            parameters['association']='raw'

            parameters['vsource']=parameters['phrasetype']+'.'+parameters['vinfix']
        elif arg=='nofunct':
            parameters['funct']=False
        elif arg=='funct':
            parameters['funct']=True
        elif arg=='diff':
            parameters['diff']=True
        elif arg=='nodiff':
            parameters['diff']=False
        elif arg=='mult':
            parameters['compop']='mult'
        elif arg=='min':
            parameters['compop']='min'
        elif arg=='gm':
            parameters['compop']='gm'
        elif arg=='add':
            parameters['compop']='add'

    return parameters
