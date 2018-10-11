from ontobio.golr.golr_associations import search_associations
from ontobio.vocabulary.relations import HomologyTypes

HOMOLOG_TYPES = [
    HomologyTypes.Ortholog.value,
    HomologyTypes.LeastDivergedOrtholog.value,
    HomologyTypes.Homolog.value,
    HomologyTypes.Paralog.value,
    HomologyTypes.InParalog.value,
    HomologyTypes.OutParalog.value,
    HomologyTypes.Ohnolog.value,
    HomologyTypes.Xenolog.value
]
INTERACTS_WITH = 'RO:0002434'

def get_association_counts(id):
    """
    For a given CURIE, get the number of associations by each category.

    Note: Experimental
    """
    count_map = {}
    subject_associations = search_associations(
        fq={'subject_closure': id},
        facet_pivot_fields=['{!stats=piv1}object_category', 'relation'],
        stats=True,
        stats_field='{!tag=piv1 calcdistinct=true distinctValues=false}object'
    )
    object_associations = search_associations(
        fq={'object_closure': id},
        facet_pivot_fields=['{!stats=piv1}subject_category', 'relation'],
        stats=True,
        stats_field='{!tag=piv1 calcdistinct=true distinctValues=false}subject'
    )
    subject_pivot_counts = subject_associations['facet_pivot']['object_category,relation']
    object_pivot_counts = object_associations['facet_pivot']['subject_category,relation']

    for category in subject_pivot_counts:
        type = category['value']
        if type == 'gene':
            count_map['gene'] = category['stats']['stats_fields']['object']['countDistinct']
            if 'pivot' in category:
                for relation in category['pivot']:
                    if relation['value'] in HOMOLOG_TYPES:
                        # homolog
                        if 'homolog' not in count_map:
                            count_map['homolog'] = relation['stats']['stats_fields']['object']['countDistinct']
                        else:
                            count_map['homolog'] += relation['stats']['stats_fields']['object']['countDistinct']
                    elif relation['value'] == INTERACTS_WITH:
                        # interaction
                        count_map['interaction'] = relation['stats']['stats_fields']['object']['countDistinct']
                    else:
                        # ignore the rest of the relation counts as they are to be aggregated at higher level
                        pass
        else:
            count_map[type] = category['stats']['stats_fields']['object']['countDistinct']

    for category in object_pivot_counts:
        type = category['value']
        if type == 'gene':
            if 'gene' not in count_map:
                count_map['gene'] = category['stats']['stats_fields']['subject']['countDistinct']
            if 'homolog' not in count_map:
                if 'pivot' in category:
                    for relation in category['pivot']:
                        if relation['value'] in HOMOLOG_TYPES:
                            # homolog
                            if 'homolog' not in count_map:
                                count_map['homolog'] = relation['stats']['stats_fields']['subject']['countDistinct']
                            else:
                                count_map['homolog'] += relation['stats']['stats_fields']['subject']['countDistinct']
                        elif relation['value'] == INTERACTS_WITH:
                            # interaction
                            count_map['interaction'] = relation['stats']['stats_fields']['object']['countDistinct']
                        else:
                            # ignore the rest of the relation counts as they are to be aggregated at higher level
                            pass
        else:
            count_map[type] = category['stats']['stats_fields']['subject']['countDistinct']

    return count_map