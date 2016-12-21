import logging

import pysolr
import json

class GolrFields:
    """
    Enumeration of fields in Golr.
    Note the Monarch golr schema is taken as canonical here
    """

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

    # golr convention: for any entity FOO, the id is denoted 'foo'
    # and the label FOO_label
    def label_field(self, f):
        return f + "_label"
    
    # golr convention: for any class FOO, the id is denoted 'foo'
    # and the cosure FOO_closure. Other closures may exist
    def closure_field(self, f):
        return f + "_closure"

# create an instance
M=GolrFields()  

# We take the monarch golr as default
# TODO: config
monarch_golr_url = "https://solr.monarchinitiative.org/solr/golr/"
monarch_solr = pysolr.Solr(monarch_golr_url, timeout=5)

def translate_objs(d,fname):
    """
    Translate a field whose value is expected to be a list
    """
    if fname not in d:
        # TODO: consider adding arg for failure on null
        return None
    
    lf = M.label_field(fname)

    v = d[fname]
    if not isinstance(v,list):
        v = [v]
    objs = [{'id': idval} for idval in v]
    # todo - labels
    
    return objs


def translate_obj(d,fname):
    """
    Translate a field value from a solr document.

    This includes special logic for when the field value
    denotes an object, here we nest it
    """
    if fname not in d:
        # TODO: consider adding arg for failure on null
        return None
    
    lf = M.label_field(fname)
    
    obj = {'id': d[fname],
            'label': d[lf],
            }

    cf = fname + "_category"
    if cf in d:
        obj['category'] = d[cf]
    
    return obj


def translate_doc(d, field_mapping=None, **kwargs):
    """
    Translate a solr document (i.e. a single result row)
    """
    if field_mapping is not None:
        for (k,v) in field_mapping.items():
            if v is not None and k is not None:
                print("TESTING FOR:"+v+" IN "+str(d))
                if v in d:
                    print("Setting field {} to {} // was in {}".format(k,d[v],v))
                    d[k] = d[v]
    subject = translate_obj(d,M.SUBJECT)
    map_identifiers_to = kwargs.get('map_identifiers')
    if map_identifiers_to:
        if M.SUBJECT_CLOSURE in d:
            subject['id'] = map_id(subject, map_identifiers_to, d[M.SUBJECT_CLOSURE])
        else:
            print("NO SUBJECT CLOSURE IN: "+str(d))
    if M.SUBJECT_TAXON in d:
        subject['taxon'] = translate_obj(d,M.SUBJECT_TAXON)
    assoc = {'id':d[M.ID],
             'subject': subject,
             'object': translate_obj(d,'object'),
             'relation': translate_obj(d,M.RELATION),
             'publications': translate_objs(d,M.SOURCE),  # note 'source' is used in the golr schema
    }
    if M.IS_DEFINED_BY in d:
        if isinstance(d[M.IS_DEFINED_BY],list):
            assoc['provided_by'] = d[M.IS_DEFINED_BY]
        else:
            # hack for GO instance
            assoc['provided_by'] = [d[M.IS_DEFINED_BY]]
    if M.EVIDENCE_OBJECT in d:
        assoc['evidence'] = d[M.EVIDENCE_OBJECT]
    # solr does not allow nested objects, so evidence graph is json-encoded
    if M.EVIDENCE_GRAPH in d:
        assoc[M.EVIDENCE_GRAPH] = json.loads(d[M.EVIDENCE_GRAPH])
    print(str(assoc))
    return assoc

def translate_docs(ds, **kwargs):
    """
    Translate a set of solr results
    """
    return [translate_doc(d, **kwargs) for d in ds]

def map_id(id, prefix, closure_list):
    """
    Map identifiers based on an equivalence closure list.
    """
    prefixc = prefix + ':'
    ids = [eid for eid in closure_list if eid.startswith(prefixc)]
    # TODO: add option to fail if no mapping, or if >1 mapping
    if len(ids) == 0:
        # default to input
        return id
    return ids[0]
               
def get_association(id, **kwargs):
    """
    Fetch an association object by ID
    """
    results = search_associations(id=id, **kwargs)
    return results['associations'][0]

def search_associations(subject_category=None,
                        object_category=None,
                        relation=None,
                        subject=None,
                        object=None,
                        subject_taxon=None,
                        invert_subject_object=False,
                        field_mapping=None,
                        solr=monarch_solr,
                        rows=10,
                        **kwargs):
    
    """
    Fetch a set of association objects based on a query
    """
    qmap = {}
    
    if subject_category is not None:
        qmap['subject_category'] = subject_category
    if object_category is not None:
        qmap['object_category'] = object_category

    if invert_subject_object:
        (subject,object) = (object,subject)
        
    if object is not None:
        # TODO: make configurable whether to use closure
        qmap['object_closure'] = object
    if subject is not None:
        # note: by including subject closure by default,
        # we automaticaly get equivalent nodes
        qmap['subject_closure'] = subject
    if subject_taxon is not None:
        qmap['subject_taxon_closure'] = subject_taxon
    if 'id' in kwargs:
        qmap['id'] = kwargs['id']
    if 'evidence' in kwargs:
        qmap['evidence_object_closure'] = kwargs['evidence']

    if field_mapping is not None:
        for (k,v) in field_mapping.items():
            if k in qmap:
                if v is None:
                    del qmap[k]
                else:
                    qmap[v] = qmap[k]
                    del qmap[k]
    
        
    # UGLY! doesn't pysolr help with this? Need to be careful with escaping?
    qstr = " AND ".join(['{}:"{}"'.format(k,v) for (k,v) in qmap.items()])

    select_fields = [
        M.ID,
        M.IS_DEFINED_BY,
        M.SOURCE,
        M.SUBJECT,
        M.SUBJECT_LABEL,
        M.SUBJECT_CLOSURE,  # TODO - only required if map_identifiers set
        M.RELATION,
        M.RELATION_LABEL,
        M.OBJECT,
        M.OBJECT_LABEL,
    ]
    if 'fl_excludes_evidence' not in kwargs or not kwargs['fl_excludes_evidence']:
        select_fields += [
            M.EVIDENCE_OBJECT,
            M.EVIDENCE_GRAPH
        ]
        
    if field_mapping is not None:
        select_fields = [ map_field(fn, field_mapping) for fn in select_fields ]    

    facet_fields = [
        M.SUBJECT_TAXON_LABEL,
        M.OBJECT_CLOSURE
    ]
    facet_fields = [ map_field(fn, field_mapping) for fn in facet_fields ]    
        
    print('Q:'+qstr)
    print('FL'+str(select_fields))
    params = {
        'q': qstr,
        'facet': 'on',
        'facet.field': facet_fields,
        'facet.limit': 25,
        'fl': ",".join(select_fields),
        'rows': rows,
    }
    results = solr.search(**params)
    fcs = results.facets
    associations = translate_docs(results.docs, field_mapping=field_mapping, **kwargs)
    return {
        'associations':associations,
        'facet_counts':fcs
    }

# GO-SPECIFIC CODE

def goassoc_fieldmap():
    """
    Returns a mapping of canonical monarch fields to golr
    """
    return {
        M.SUBJECT: 'bioentity',
        M.SUBJECT_CLOSURE: 'bioentity',
        M.SUBJECT_LABEL: 'bioentity_label',
        M.SUBJECT_TAXON: 'taxon',
        M.SUBJECT_TAXON_LABEL: 'taxon_label',
        M.OBJECT: 'annotation_class',
        M.OBJECT_LABEL: 'annotation_class_label',
        M.SUBJECT_CATEGORY: None,
        M.OBJECT_CATEGORY: None,
        M.IS_DEFINED_BY: 'assigned_by'
    }

def map_field(fn, m) :
    if m is None:
        return fn
    if fn in m:
        return m[fn]
    else:
        return fn

# TODO: unify this with the monarch-specific instance
# note that longer term the goal is to unify the go and mon
# golr schemas more. For now the simplest path is
# to introduce this extra method, and 'mimic' the monarch one,
# at the risk of some duplication of code and inelegance

def search_associations_go(
        subject_category=None,
        object_category=None,
        relation=None,
        subject=None,
        **kwargs):
    go_golr_url = "http://golr.geneontology.org/solr/"
    go_solr = pysolr.Solr(go_golr_url, timeout=5)
    return search_associations(subject_category,
                               object_category,
                               relation,
                               subject,
                               solr=go_solr,
                               field_mapping=goassoc_fieldmap(),
                               **kwargs)
