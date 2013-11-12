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

    for arg in args:
        if arg=='testing':
            parameters['testing']=True
        elif arg =='extract':
            parameters['extract']=True
        elif arg =='build':
            parameters['build']=True
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
            parameters['totalfile']='events.strings_domcol'
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
            parameters['altdepfile']='wikipedia_nounsdeps_t100.pbfiltered'
            parameters['depfile']='wikipedia_adjsdeps_t100.pbfiltered.'+parameters['usefile']
            parameters['totalfile']='events.strings_depcol'
            parameters['adjlist']=True
            parameters['allheads']=True
            parameters['collocatefile']=['multiwords.train','multiwords.test','multiwords.spare']
            parameters['freqthresh']=100
            parameters['featurematch']='amod-HEAD'
            parameters['nfmod']=True
        elif arg =='NFmod':
            parameters['nfmod']=True
    return parameters
