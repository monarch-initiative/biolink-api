import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
import pysolr
import json

# CV
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
ID='id'
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

# TODO: config
golr_url = "https://solr.monarchinitiative.org/solr/golr/"
solr = pysolr.Solr(golr_url, timeout=5)

def translate_obj(d,name):
    lf = name + "_label"
    
    obj = {'id': d[name],
            'label': d[lf],
            }

    cf = name + "_category"
    if cf in d:
        obj['category'] = d[cf]
    
    return obj


def translate_doc(d):
    subject = translate_obj(d,SUBJECT)
    if SUBJECT_TAXON in d:
        subject['taxon'] = translate_obj(d,SUBJECT_TAXON)
    assoc = {'id':1,
             'subject': subject,
             'object': translate_obj(d,'object'),
             'sources': d[IS_DEFINED_BY],
             'evidence': d[EVIDENCE_OBJECT]
    }
    if EVIDENCE_GRAPH in d:
        assoc[EVIDENCE_GRAPH] = json.loads(d[EVIDENCE_GRAPH])
    return assoc

def translate_docs(ds):
    return [translate_doc(d) for d in ds]


def get_associations(subject_category, object_category, args, id=None):

    sub_q = args.get('subject')
    obj_q = args.get('object')
    tax_q = args.get('subject_taxon')

    if id is not None:
        sub_q = id
    
    qmap = { 'subject_category' : subject_category, 'object_category' : 'phenotype' }
    if obj_q is not None:
        # TODO: make configurable whether to use closure
        qmap['object_closure'] = obj_q
    if sub_q is not None:
        qmap['subject_closure'] = sub_q
    if tax_q is not None:
        qmap['subject_taxon_closure'] = tax_q
            
    qstr = " AND ".join(['{}:"{}"'.format(k,v) for (k,v) in qmap.items()])
    results = solr.search(q=qstr,
                          fl="", rows=10)

    associations = translate_docs(results)
    return associations
