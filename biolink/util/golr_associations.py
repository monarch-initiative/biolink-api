import logging

import pysolr
import json

# CV
class GolrFields:
    ID='id'
    SOURCE='source'
    OBJECT_CLOSURE='object_closure'
    SOURCE_CLOSURE_MAP='source_closure_map'
    SUBJECT_TAXON_CLOSURE_LABEL='subject_taxon_closure_label'
    SUBJECT_GENE_CLOSURE_MAP='subject_gene_closure_map'
    EVIDENCE_OBJECT='evidence_object'
    SUBJECT_TAXON_LABEL_SEARCHABLE='subject_taxon_label_searchable'
    IS_DEFINED_BY='is_defined_by'
    SUBJECT_GENE_CLOSURE_LABEL='subject_gene_closure_label'
    EVIDENCE_OBJECT_CLOSURE_LABEL='evidence_object_closure_label'
    SUBJECT_TAXON_CLOSURE='subject_taxon_closure'
    OBJECT_LABEL='object_label'
    SUBJECT_CATEGORY='subject_category'
    SUBJECT_GENE_LABEL='subject_gene_label'
    SUBJECT_TAXON_CLOSURE_LABEL_SEARCHABLE='subject_taxon_closure_label_searchable'
    SUBJECT_GENE_CLOSURE='subject_gene_closure'
    SUBJECT_GENE_LABEL_SEARCHABLE='subject_gene_label_searchable'
    SUBJECT='subject'
    SUBJECT_LABEL='subject_label'
    SUBJECT_CLOSURE_LABEL_SEARCHABLE='subject_closure_label_searchable'
    OBJECT_CLOSURE_LABEL_SEARCHABLE='object_closure_label_searchable'
    EVIDENCE_OBJECT_CLOSURE='evidence_object_closure'
    OBJECT_CLOSURE_LABEL='object_closure_label'
    EVIDENCE_CLOSURE_MAP='evidence_closure_map'
    SUBJECT_CLOSURE_LABEL='subject_closure_label'
    SUBJECT_GENE='subject_gene'
    SUBJECT_TAXON='subject_taxon'
    OBJECT_LABEL_SEARCHABLE='object_label_searchable'
    OBJECT_CATEGORY='object_category'
    SUBJECT_TAXON_CLOSURE_MAP='subject_taxon_closure_map'
    QUALIFIER='qualifier'
    SUBJECT_TAXON_LABEL='subject_taxon_label'
    SUBJECT_CLOSURE_MAP='subject_closure_map'
    SUBJECT_ORTHOLOG_CLOSURE='subject_ortholog_closure'
    EVIDENCE_GRAPH='evidence_graph'
    SUBJECT_CLOSURE='subject_closure'
    OBJECT='object'
    OBJECT_CLOSURE_MAP='object_closure_map'
    SUBJECT_LABEL_SEARCHABLE='subject_label_searchable'
    EVIDENCE_OBJECT_CLOSURE_MAP='evidence_object_closure_map'
    EVIDENCE_OBJECT_LABEL='evidence_object_label'
    _VERSION_='_version_'
    SUBJECT_GENE_CLOSURE_LABEL_SEARCHABLE='subject_gene_closure_label_searchable'
    
    RELATION='relation'
    RELATION_LABEL='relation_label'

    def label_field(self, f):
        return f + "_label"
  
M=GolrFields()  
  
# TODO: config
golr_url = "https://solr.monarchinitiative.org/solr/golr/"
solr = pysolr.Solr(golr_url, timeout=5)

# TODO: move
search_url = "https://solr.monarchinitiative.org/solr/search/"
#solr = pysolr.Solr(golr_url, timeout=5)

def translate_objs(d,name):
    if name not in d:
        # TODO: consider adding arg for failure on null
        return None
    
    lf = M.label_field(name)
    
    objs = [{'id': idval} for idval in d[name]]
    # todo - labels
    
    return objs


def translate_obj(d,name):
    if name not in d:
        # TODO: consider adding arg for failure on null
        return None
    
    lf = M.label_field(name)
    
    obj = {'id': d[name],
            'label': d[lf],
            }

    cf = name + "_category"
    if cf in d:
        obj['category'] = d[cf]
    
    return obj


def translate_doc(d, **kwargs):
    subject = translate_obj(d,M.SUBJECT)
    if M.SUBJECT_TAXON in d:
        subject['taxon'] = translate_obj(d,M.SUBJECT_TAXON)
    assoc = {'id':d[M.ID],
             'subject': subject,
             'object': translate_obj(d,'object'),
             'relation': translate_obj(d,M.RELATION),
             'publications': translate_objs(d,M.SOURCE),  # note 'source' is used in the golr schema
             'provided_by': d[M.IS_DEFINED_BY]
    }
    if M.EVIDENCE_OBJECT in d:
        assoc['evidence'] = d[M.EVIDENCE_OBJECT]
    # solr does not allow nested objects, so evidence graph is json-encoded
    if M.EVIDENCE_GRAPH in d:
        assoc[M.EVIDENCE_GRAPH] = json.loads(d[M.EVIDENCE_GRAPH])
    return assoc

def translate_docs(ds, **kwargs):
    return [translate_doc(d, **kwargs) for d in ds]


# @Deprecated
def get_associations(id, **kwargs):
    return search_associations(id=id, **kwargs)
def get_association(id, **kwargs):
    results = search_associations(id=id, **kwargs)
    return results['associations'][0]

def search_associations(subject_category=None,
                        object_category=None,
                        relation=None,
                        subject=None,
                        object=None,
                        subject_taxon=None,
                        **kwargs):
    
    qmap = {}
    if subject_category is not None:
        qmap['subject_category'] = subject_category
    if object_category is not None:
        qmap['object_category'] = object_category
    
    if object is not None:
        # TODO: make configurable whether to use closure
        qmap['object_closure'] = object
    if subject is not None:
        qmap['subject_closure'] = subject
    if subject_taxon is not None:
        qmap['subject_taxon_closure'] = subject_taxon
    if 'id' in kwargs:
        qmap['id'] = kwargs['id']

    # UGLY! doesn't pysolr help with this? Need to be careful with escaping?
    qstr = " AND ".join(['{}:"{}"'.format(k,v) for (k,v) in qmap.items()])
    print('Q:'+qstr)
    select_fields = [
        M.ID,
        M.IS_DEFINED_BY,
        M.SOURCE,
        M.SUBJECT,
        M.SUBJECT_LABEL,
        M.RELATION,
        M.RELATION_LABEL,
        M.OBJECT,
        M.OBJECT_LABEL,
    ]
    if 'exclude_evidence' not in kwargs or not kwargs['exclude_evidence']:
        select_fields += [
            M.EVIDENCE_OBJECT,
            M.EVIDENCE_GRAPH
        ]

    params = {
        'q': qstr,
        'facet': 'on',
        'facet.field': [M.SUBJECT_TAXON_LABEL],
        'facet.limit': 25,
        'fl': ",".join(select_fields),
        'rows': 10,
    }
    results = solr.search(**params)
    fcs = results.facets
    associations = translate_docs(results.docs, **kwargs)
    return {
        'associations':associations,
        'facet_counts':fcs
    }
