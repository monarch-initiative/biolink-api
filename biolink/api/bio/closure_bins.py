
closure_map = {
    'UBERON:0001434PHENOTYPE': 'Skeletal system',
    'UBERON:0002101PHENOTYPE': 'Limbs',
    'UBERON:0001016PHENOTYPE': 'Nervous system',
    'UBERON:0007811PHENOTYPE': 'Head or neck',
    'MP:0005376': 'Metabolism/homeostasis',
    'UBERON:0004535PHENOTYPE': 'Cardiovascular system',
    'UBERON:0002416PHENOTYPE': 'Integument',
    'UBERON:0004122PHENOTYPE': 'Genitourinary system',
    'UBERON:0000970PHENOTYPE': 'Eye',
    'UBERON:0001015PHENOTYPE': 'Musculature',
    'MPATH:218PHENOTYPE': 'Neoplasm',
    'UBERON:0001007PHENOTYPE': 'Digestive system',
    'UBERON:0002405PHENOTYPE': 'Immune system',
    'UBERON:0002390PHENOTYPE': 'Blood and blood-forming tissues',
    'UBERON:0000949PHENOTYPE': 'Endocrine',
    'UBERON:0001004PHENOTYPE': 'Respiratory system',
    'UBERON:0001690PHENOTYPE': 'Ear',
    'UBERON:0002384PHENOTYPE': 'Connective tissue',
    'UBERON:0000323PHENOTYPE': 'Prenatal development or birth',
    'GO:0040007PHENOTYPE': 'Growth',
    'HP:0025142': 'Symptom',
    'UBERON:0002224PHENOTYPE': 'Thoracic cavity',
    'UBERON:0000310PHENOTYPE': 'Breast',
    'HP:0001608': 'Voice',
    'CL:0000000PHENOTYPE': 'Cellular'
}

def create_closure_bin(fcmap={}):
    """
    Given a facet count dict from golr_query (i.e. map of class ID to count)
    return a new dict that maps original IDs to high level text descriptors.

    It is assumed that the input dict is complete (with closed world assumption).
    i.e. grouping terms already included, and if not included assume = 0

    Return: Tuple of two dictionaries, a label-count map and id-count map
    """
    lmap = {}
    idmap = {}
    for curie, label in closure_map.items():
        lmap[label] = 0
        idmap[curie] = 0
    for k,v in fcmap.items():
        if k in closure_map:
            label = closure_map[k]

            # we expect duplicates due to merging
            # of different ontologies. We take the higher value
            if label in lmap:
                if lmap[label] > v:
                    continue

            lmap[label] = v
            idmap[k] = v
    return lmap, idmap
