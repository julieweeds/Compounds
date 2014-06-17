__author__ = 'juliewe'

import compare



if __name__=='__main__':

    #met='path'
    met='path'
    #words=['ability/N','sturdiness/N','aptitude/N','physical_ability/N','natural_ability/N','quickness/N']
    words=['herbaceous_plant/N','industrial_plant/N','plant/N','shrub/N','succulent/N','refinery/N']
    for word1 in words:
        for word2 in words:

            print word1,word2,compare.wnsim(word1,word2,metric=met)