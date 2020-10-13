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
    'publication_variant': {
        'publication': 'variant',
        'variant': 'publication'
    },
    'gene_homology': {
        'gene': 'homolog'
    },
    'publication_gene': {
        'publication': 'gene',
        'gene': 'publication'
    },
    'gene_interaction': {
        'gene': 'interaction',
        'ortholog': 'interaction'
    },
    'variant_phenotype':{
        'variant': 'phenotype',
        'phenotype': 'variant'
    },
    'genotype_gene': {
        'genotype': 'gene',
        'gene': 'genotype'
    },
    'gene_anatomy': {
        'gene': 'anatomy',
        'anatomy': 'gene',
        'ortholog': 'anatomy'
    },
    'variant_gene': {
        'variant': 'gene',
        'gene': 'variant'
    },
    "variant_genotype": {
        'variant': 'genotype',
        'genotype': 'variant',
        'model': 'variant'

    },
    "gene_function": {
        'gene': 'function',
        'function': 'gene',
        'goterm': 'gene',
        'ortholog': 'function'
    },
    "model_gene": {
        'model': 'gene',
        'gene': 'model'
    },
    "genotype_phenotype": {
        'genotype': 'phenotype',
        'phenotype': 'genotype',
        'model': 'phenotype'
    },
    'model_variant': {
        'model': 'variant',
        'variant': 'model'
    },
    "gene_phenotype": {
        'gene': 'phenotype',
        'phenotype': 'gene',
        'ortholog': 'phenotype'
    },
    "publication_phenotype": {
        'publication': 'phenotype',
        'phenotype': 'publication'
    },
    'publication_genotype': {
        'publication': 'genotype',
        'genotype': 'publication'
    },
    "gene_pathway": {
        'gene': 'pathway',
        'pathway': 'gene',
        'ortholog': 'pathway'
    },
    "publication_disease": {
        'publication': 'disease',
        'disease': 'publication'
    },
    "disease_phenotype": {
        'disease': 'phenotype',
        'phenotype': 'disease'
    },
    "variant_disease": {
        'variant': 'disease',
        'disease': 'variant'
    },
    "pathway_phenotype": {
        'pathway': 'phenotype',
        'phenotype': 'pathway'
    },
    "disease_pathway": {
        'pathway': 'disease',
        'disease': 'pathway'
    },
    "gene_temporal": {},
    "model_case": {
        'model': 'case',
        'case': 'model'
    },
    "model_disease": {
        'model': 'disease',
        'disease': 'model'
    },
    "publication_model": {
        'publication': 'model',
        'model': 'publication'
    },
    "marker_disease": {
        'gene': 'correlated-disease',
        'disease': 'correlated-gene',
        'ortholog': 'disease'
    },
    "case_disease": {
        'case': 'disease',
        'disease': 'case'
    },
    "gene_disease": {
        'gene': 'causal-disease',
        'disease': 'causal-gene',
        'ortholog': 'disease'
    },
    "case_variant": {
        'case': 'variant',
        'variant': 'case'
    },
    "case_genotype": {
        'case': 'genotype',
        'genotype': 'case'
    },
    "model_genotype": {
        'model': 'genotype',
        'genotype': 'model'
    },
    "genotype_disease": {
        'genotype': 'disease',
        'disease': 'genotype'
    },
    "case_gene": {
        'case': 'gene',
        'gene': 'case'
    },
    "case_phenotype": {
        'case': 'phenotype',
        'phenotype': 'case'
    },
    "chemical_disease": {
        'chemical': 'disease',
        'disease': 'chemical'
    }
}

EXCLUDE_LIST = ['ortholog-homolog']


def get_association_counts(bioentity_id, bioentity_type=None, distinct_counts=False):
    """
    For a given CURIE, get the number of associations by each category.
    """
    count_map = {}
    source_count = {}
    # get counts where bioentity_id is the subject

    if distinct_counts:
        subject_associations = search_associations(
            fq={'subject_closure': bioentity_id},
            facet_pivot_fields=['{!stats=piv1}association_type', 'object_taxon'],
            stats=True,
            rows=0,
            facet_fields=['is_defined_by'],
            facet_limit='100',
            stats_field=['{!tag=piv1 calcdistinct=true distinctValues=false}object']
        )
    else:
        subject_associations = search_associations(
            fq={'subject_closure': bioentity_id},
            facet_pivot_fields=['{!stats=piv1}association_type', 'object_taxon'],
            stats=True,
            rows=0,
            facet_fields=['is_defined_by'],
            facet_limit='100',
            stats_field=['{!tag=piv1 countDistinct=false}object']
        )
    source_count = subject_associations['facet_counts']['is_defined_by']
    subject_facet_pivot = subject_associations['facet_pivot']['association_type,object_taxon']
    parse_facet_pivot(subject_facet_pivot, bioentity_type, count_map, distinct_counts=distinct_counts)

    # get counts where bioentity_id is the object
    if distinct_counts:
        object_associations = search_associations(
            fq={'object_closure': bioentity_id},
            facet_pivot_fields=['{!stats=piv1}association_type', 'subject_taxon'],
            stats=True,
            rows=0,
            facet_fields=['is_defined_by'],
            facet_limit='100',
            stats_field=['{!tag=piv1 calcdistinct=true distinctValues=false}subject']
        )
    else:
        object_associations = search_associations(
            fq={'object_closure': bioentity_id},
            facet_pivot_fields=['{!stats=piv1}association_type', 'subject_taxon'],
            stats=True,
            rows=0,
            facet_fields=['is_defined_by'],
            facet_limit='100',
            stats_field=['{!tag=piv1 countDistinct=false}subject']
        )

    for src, count in object_associations['facet_counts']['is_defined_by'].items():
        if src in source_count:
            source_count[src] += count
        else:
            source_count[src] = count

    object_facet_pivot = object_associations['facet_pivot']['association_type,subject_taxon']
    parse_facet_pivot(object_facet_pivot, bioentity_type, count_map, distinct_counts=distinct_counts)

    if bioentity_type == 'gene':
        # get counts for ortholog-x associations
        bioentity_type = type_prefix = 'ortholog'
        ortholog_count_map = {}
        if distinct_counts:
            ortholog_associations = search_associations(
                fq={'subject_ortholog_closure': bioentity_id},
                facet_pivot_fields=['{!stats=piv1}association_type', 'object_taxon'],
                stats=True,
                rows=0,
                facet_fields=[],
                stats_field=['{!tag=piv1 calcdistinct=true distinctValues=false}object']
            )
        else:
            ortholog_associations = search_associations(
                fq={'subject_ortholog_closure': bioentity_id},
                facet_pivot_fields=['{!stats=piv1}association_type', 'object_taxon'],
                stats=True,
                rows=0,
                facet_fields=[],
                stats_field=['{!tag=piv1 countDistinct=false}object']
            )
        ortholog_facet_pivot = ortholog_associations['facet_pivot']['association_type,object_taxon']
        parse_facet_pivot(ortholog_facet_pivot, bioentity_type, ortholog_count_map, type_prefix, distinct_counts=distinct_counts)
        final_count_map = {**count_map, **ortholog_count_map}
    else:
        final_count_map = count_map

    final_count_map['sources'] = source_count

    for x in EXCLUDE_LIST:
        if x in final_count_map:
            final_count_map.pop(x)

    return final_count_map


def parse_facet_pivot(facet_pivot, bioentity_type, count_map, type_prefix=None, distinct_counts=False):

    if count_map is None:
        count_map = {}

    for category_pivot in facet_pivot:
        type = category_pivot['value']
        if bioentity_type not in CATEGORY_NAME_MAP[type]:
            # ignore this count type
            continue
        k = CATEGORY_NAME_MAP[type][bioentity_type]
        if type_prefix:
            k = "{}-{}".format(type_prefix, k)

        if k not in count_map:
            count_map[k] = {}
        if k == 'homolog' and k in count_map and 'counts' in count_map[k]:
            # ignore, to avoid double counting
            continue

        category_stats = category_pivot['stats']['stats_fields']
        key = None
        if 'subject' in category_stats:
            key = 'subject'
        elif 'object' in category_stats:
            key = 'object'
        if distinct_counts:
            category_counts = category_stats[key]['countDistinct']
        else:
            category_counts = category_pivot['count']

        if 'counts' in count_map[k]:
            count_map[k]['counts'] += category_counts
        else:
            count_map[k] = {
                'counts': category_counts
            }

        if 'pivot' in category_pivot:
            # taxon pivot
            taxon_pivot = category_pivot['pivot']
            taxon_counts = parse_taxon_pivot(taxon_pivot, key, distinct_counts)
            if 'counts_by_taxon' in count_map[k]:
                taxon_counts = merge_counts(count_map[k]['counts_by_taxon'], taxon_counts)
            count_map[k]['counts_by_taxon'] = taxon_counts

    return count_map


def parse_taxon_pivot(taxon_pivot, key, distinct_counts=False):
    counts_map = {}
    for t in taxon_pivot:
        taxon = t['value']
        if distinct_counts:
            counts = t['stats']['stats_fields'][key]['countDistinct']
        else:
            counts = t['count']
        counts_map[taxon] = counts
    return counts_map

def merge_counts(d1, d2):
    d = {}
    d1_key_set = set(x for x in d1.keys())
    d2_key_set = set(x for x in d2.keys())
    all_keys = d1_key_set | d2_key_set
    for k in all_keys:
        count = 0
        if k in d1:
            count += d1[k]
        if k in d2:
            count += d2[k]
        d[k] = count
    return d
