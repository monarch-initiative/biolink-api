
closure_map = {
    'HP:0000119' : 'genitourinary',
    'HP:0000152' : 'head or neck',
    'HP:0000478' : 'eye',
    'HP:0000598' : 'ear',
    'HP:0000707' : 'nervous system',
    'HP:0000769' : 'breast',
    'HP:0000818' : 'endocrine',
    'HP:0000924' : 'skeletal',
    'HP:0001197' : 'prenatal development or birth',
    'HP:0001507' : 'growth',
    'HP:0001574' : 'integument',
    'HP:0001608' : 'voice',
    'HP:0001626' : 'cardiovascular',
    'HP:0001871' : 'hematopoetic',
    'HP:0001939' : 'metabolism/homeostasis',
    'HP:0002086' : 'respiratory',
    'HP:0002664' : 'neoplasm',
    'HP:0002715' : 'immune',
    'HP:0003011' : 'musculature',
    'HP:0003549' : 'connective tissue',
    'HP:0025031' : 'digestive',
    'HP:0025142' : 'constitutional',
    'HP:0025354' : 'cellular',
    'HP:0040064' : 'limbs',
    'HP:0045027' : 'thoracic cavity',
    'MP:0001186' : 'pigmentation',
    'MP:0002006' : 'neoplasm',
    'MP:0002873' : 'normal',
    'MP:0003012' : 'no phenotypic analysis',
    'MP:0003631' : 'nervous system',
    'MP:0005367' : 'renal/urinary system',
    'MP:0005369' : 'muscle',
    'MP:0005370' : 'liver/biliary system',
    'MP:0005371' : 'limbs/digits/tail',
    'MP:0005375' : 'adipose tissue',
    'MP:0005376' : 'homeostasis/metabolism',
    'MP:0005377' : 'hearing/vestibular/ear',
    'MP:0005378' : 'growth/size/body region',
    'MP:0005379' : 'endocrine/exocrine gland',
    'MP:0005380' : 'embryo',
    'MP:0005381' : 'digestive/alimentary',
    'MP:0005382' : 'craniofacial',
    'MP:0005384' : 'cellular',
    'MP:0005385' : 'cardiovascular system',
    'MP:0005386' : 'behavior/neurological',
    'MP:0005387' : 'immune system',
    'MP:0005388' : 'respiratory system',
    'MP:0005389' : 'reproductive system',
    'MP:0005390' : 'skeleton',
    'MP:0005391' : 'vision/eye',
    'MP:0005394' : 'taste/olfaction',
    'MP:0005397' : 'hematopoietic system',
    'MP:0010768' : 'mortality/aging',
    'MP:0010771' : 'integument'
}

def create_closure_bin(fcmap={}):
    """
    Given a facet count dict from golr_query (i.e. map of class ID to count)
    return a new dict that maps original IDs to high level text descriptors.

    It is assumed that the input dict is complete (with closed world assumption).
    i.e. grouping terms already included, and if not included assume = 0
    """
    lmap = {}
    for v in closure_map.values():
        lmap[v] = 0
    for k,v in fcmap.items():
        if k in closure_map:
            label = closure_map[k]

            # we expect duplicates due to merging
            # of different ontologies. We take the higher value
            if label in lmap:
                if lmap[label] > v:
                    continue

            lmap[label] = v
    return lmap
