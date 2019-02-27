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

CATEGORY_NAME_MAP = {
    'gene': 'gene',
    'interaction': 'interaction',
    'homolog': 'homolog',
    'genotype': 'genotype',
    'phenotype': 'phenotype',
    'anatomical entity': 'anatomy',
    'biological process': 'function',
    'pathway': 'pathway',
    'disease': 'disease',
    'publication': 'publication',
    'variant': 'variant',
    'model': 'model',
    'case': 'case',
    'substance': 'substance',
    'ortholog-interaction': 'ortholog-interaction',
    'ortholog-genotype': 'ortholog-genotype',
    'ortholog-phenotype': 'ortholog-phenotype',
    'ortholog-anatomical entity': 'ortholog-anatomy',
    'ortholog-biological process': 'ortholog-function',
    'ortholog-pathway': 'ortholog-pathway',
    'ortholog-disease': 'ortholog-disease',
    'ortholog-publication': 'ortholog-publication',
    'ortholog-variant': 'ortholog-variant',
    'ortholog-model': 'ortholog-model',
    'ortholog-case': 'ortholog-case',
    'ortholog-substance': 'ortholog-substance'
}

def get_association_counts(bioentity_id, bioentity_type=None):
    """
    For a given CURIE, get the number of associations by each category.
    """
    count_map = {}
    subject_associations = search_associations(
        fq={'subject_closure': bioentity_id},
        facet_pivot_fields=['{!stats=piv1}object_category', 'relation'],
        stats=True,
        stats_field=['{!tag=piv1 calcdistinct=true distinctValues=false}object']
    )
    object_associations = search_associations(
        fq={'object_closure': bioentity_id},
        facet_pivot_fields=['{!stats=piv1}subject_category', 'relation'],
        stats=True,
        stats_field=['{!tag=piv1 calcdistinct=true distinctValues=false}subject']
    )
    subject_facet_pivot = subject_associations['facet_pivot']['object_category,relation']
    object_facet_pivot = object_associations['facet_pivot']['subject_category,relation']
    parse_facet_pivot(subject_facet_pivot, count_map)
    parse_facet_pivot(object_facet_pivot, count_map)

    if bioentity_type == 'gene':
        if CATEGORY_NAME_MAP['gene'] in count_map:
            count_map.pop(CATEGORY_NAME_MAP['gene'])
        # get counts for all ortholog associations
        ortholog_associations = search_associations(
            fq={'subject_ortholog_closure': bioentity_id},
            facet_pivot_fields=['{!stats=piv1}object_category', 'relation'],
            stats=True,
            stats_field=['{!tag=piv1 calcdistinct=true distinctValues=false}object']
        )

        ortholog_pivot_counts = ortholog_associations['facet_pivot']['object_category,relation']
        for category in ortholog_pivot_counts:
            type = category['value']
            if type == 'gene':
                if 'pivot' in category:
                    for relation in category['pivot']:
                        if relation['value'] == INTERACTS_WITH:
                            # Ortholog-Interactions
                            count_map[CATEGORY_NAME_MAP['ortholog-interaction']] = relation['stats']['stats_fields']['object']['countDistinct']
            else:
                key = 'ortholog-{}'.format(type)
                count_map[CATEGORY_NAME_MAP[key]] = category['stats']['stats_fields']['object']['countDistinct']

    return count_map

def parse_facet_pivot(facet_pivot, count_map=None):

    if count_map is None:
        count_map = {}

    for category in facet_pivot:
        type = category['value']
        stats_fields = category['stats']['stats_fields']
        key = None
        if 'subject' in stats_fields:
            key = 'subject'
        elif 'object' in stats_fields:
            key = 'object'

        if type == 'gene':
            if CATEGORY_NAME_MAP[type] in count_map:
                # avoid counting twice for 'gene'
                continue
            count_map[CATEGORY_NAME_MAP[type]] = stats_fields[key]['countDistinct']
            if 'pivot' in category:
                for relation in category['pivot']:
                    relation_stats_fields = relation['stats']['stats_fields']
                    if relation['value'] in HOMOLOG_TYPES:
                        if CATEGORY_NAME_MAP['homolog'] in count_map:
                            count_map[CATEGORY_NAME_MAP['homolog']] += relation_stats_fields[key]['countDistinct']
                        else:
                            count_map[CATEGORY_NAME_MAP['homolog']] = relation_stats_fields[key]['countDistinct']
                    elif relation['value'] == INTERACTS_WITH:
                        count_map[CATEGORY_NAME_MAP['interaction']] = relation_stats_fields[key]['countDistinct']
        else:
            count_map[CATEGORY_NAME_MAP[type]] = stats_fields[key]['countDistinct']

    return count_map
