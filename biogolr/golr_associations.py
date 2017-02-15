"""Wrapper for a Solr index following Golr conventions

Intended to work with:

 * Monarch golr instance
 * AmiGO/GO golr instance

# Conventions

Documents follow either entity or association patterns.

## Associations

Connects some kind of *subject* to an *object* via a *relation*, this
should be read as any RDF triple.

The subject may be a molecular biological entity such as a gene, or an
ontology class. The distinction between these two may be malleable.

The object is typically an ontology class, but not
always. E.g. gene-gene interactions or homology for exceptions.

An association also has evidence plus various provenance metadata.

In Monarch, the evidence is modeled as a graph encoded as a JSON blob;

In AmiGO, we follow the GAF data model where it is assumed evidence is
simple as does not follow chains, there is assumed to be one evidence
object for the intermediate entity.

### Entities

TODO

"""
import logging

import pysolr
import json

import math ### TODO - move?

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
    
    #lf = M.label_field(fname)

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
    
    obj = {'id': d[fname]}

    if lf in d:
        obj['label'] = d[lf]
    
    cf = fname + "_category"
    if cf in d:
        obj['categories'] = [d[cf]]
    
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
    assoc = {'id':d.get(M.ID),
             'subject': subject,
             'object': translate_obj(d,'object'),
             'relation': translate_obj(d,M.RELATION),
             'publications': translate_objs(d,M.SOURCE),  # note 'source' is used in the golr schema
    }
    if M.OBJECT_CLOSURE in d:
        assoc['object_closure'] = d.get(M.OBJECT_CLOSURE)
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
    return assoc

def translate_docs(ds, **kwargs):
    """
    Translate a set of solr results
    """
    return [translate_doc(d, **kwargs) for d in ds]


def translate_docs_compact(ds, **kwargs):
    """
    Translate golr association documents to a compact representation
    """
    amap = {}
    for d in ds:
        rel = d.get(M.RELATION)
        k = (d[M.SUBJECT],rel)
        if k not in amap:
            amap[k] = {'subject':d[M.SUBJECT],
                       'relation':rel,
                       'objects': []}
        amap[k]['objects'].append(d[M.OBJECT])
    return list(amap.values())

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
                        subjects=None,
                        object=None,
                        objects=None,
                        subject_direct=False,
                        subject_taxon=None,
                        object_taxon=None,
                        invert_subject_object=False,
                        use_compact_associations=False,
                        include_raw=False,
                        field_mapping=None,
                        solr=monarch_solr,
                        select_fields=None,
                        fetch_objects=False,
                        slim=[],
                        json_facet=None,
                        facet_fields = [
                            M.SUBJECT_TAXON_LABEL,
                            M.OBJECT_CLOSURE
                        ],
                        facet_field_limits = None,
                        facet_limit=25,
                        facet_mincount=1,
                        facet_pivot_fields = [],
                        rows=10,
                        **kwargs):
    
    """Fetch a set of association objects based on a query.

    Arguments
    ---------

    fetch_objects : bool

        we frequently want a list of distinct association objects (in
        the RDF sense).  for example, when querying for all phenotype
        associations for a gene, it is convenient to get a list of
        distinct phenotype terms. Although this can be obtained by
        iterating over the list of associations, it can be expensive
        to obtain all associations. 

        Results are in the 'objects' field

    slim : List

        a list of either class ids (or in future subset ids), used to
        map up (slim) objects in associations. This will populate
        an additional 'slim' field in each association object corresponding
        to the slimmed-up value(s) from the direct objects.
        If fetch_objects is passed, this will be populated with slimmed IDs.

    use_compact_associations : bool

        If true, then the associations list will be false, instead
        compact_associations contains a more compact representation
        consisting of objects with (subject, relation and objects)

    """
    fq = {}

    # temporary: for querying go solr, map fields
    if object_category is not None and object_category == 'function':
        go_golr_url = "http://golr.berkeleybop.org/solr/"
        solr = pysolr.Solr(go_golr_url, timeout=5)
        field_mapping=goassoc_fieldmap()
        fq['document_category'] = 'annotation'
        print('MGI hack: '+str(subject))
        if subject is not None and subject.startswith('MGI:'):
            subject = 'MGI:' + subject
    
    # typically information is stored one-way, e.g. model-disease;
    # sometimes we want associations from perspective of object
    if invert_subject_object:
        (subject,object) = (object,subject)
        (subject_category,object_category) = (object_category,subject_category)
        (subject_taxon,object_taxon) = (object_taxon,subject_taxon)

        
    if subject_category is not None:
        fq['subject_category'] = subject_category
    if object_category is not None:
        fq['object_category'] = object_category

        
    if object is not None:
        # TODO: make configurable whether to use closure
        fq['object_closure'] = object
    if subject is not None:
        # note: by including subject closure by default,
        # we automaticaly get equivalent nodes
        if subject_direct:
            fq['subject'] = subject
        else:
            fq['subject_closure'] = subject
    if subjects is not None:
        # lists are assumed to be disjunctive
        if subject_direct:
            fq['subject'] = subjects
        else:
            fq['subject_closure'] = subjects
    if objects is not None:
        # lists are assumed to be disjunctive
        fq['object_closure'] = objects
    if relation is not None:
        fq['relation_closure'] = relation
    if subject_taxon is not None:
        fq['subject_taxon_closure'] = subject_taxon
    if 'id' in kwargs:
        fq['id'] = kwargs['id']
    if 'evidence' in kwargs and kwargs['evidence'] is not None:
        fq['evidence_object_closure'] = kwargs['evidence']
    if 'exclude_automatic_assertions' in kwargs and kwargs['exclude_automatic_assertions']:
        fq['-evidence_object_closure'] = 'ECO:0000501'
    if 'pivot_subject_object' in kwargs and kwargs['pivot_subject_object']:
        facet_pivot_fields = [M.SUBJECT, M.OBJECT]
    
        
    if field_mapping is not None:
        for (k,v) in field_mapping.items():
            if k in fq:
                if v is None:
                    del fq[k]
                else:
                    fq[v] = fq[k]
                    del fq[k]
    

    filter_queries = []
    qstr = "*:*"
    filter_queries = [ '{}:{}'.format(k,solr_quotify(v))  for (k,v) in fq.items()]

    # unless caller specifies a field list, use default
    if select_fields is None:
        select_fields = [
            M.ID,
            M.IS_DEFINED_BY,
            M.SOURCE,
            M.SUBJECT,
            M.SUBJECT_LABEL,
            M.SUBJECT_CLOSURE,  # TODO - only required if map_identifiers set
            M.SUBJECT_TAXON,
            M.SUBJECT_TAXON_LABEL,
            M.RELATION,
            M.RELATION_LABEL,
            M.OBJECT,
            M.OBJECT_LABEL,
        ]
        if 'unselect_evidence' not in kwargs or not kwargs['unselect_evidence']:
            select_fields += [
                M.EVIDENCE_OBJECT,
                M.EVIDENCE_GRAPH
            ]
        
    if field_mapping is not None:
        select_fields = [ map_field(fn, field_mapping) for fn in select_fields ]    

    if slim is not None and len(slim)>0:
        select_fields.append(M.OBJECT_CLOSURE)
        
    facet_fields = [ map_field(fn, field_mapping) for fn in facet_fields ]    
        
    #print('FL'+str(select_fields))
    is_unlimited = False
    if rows < 0:
        is_unlimited = True
        rows = 100000
    params = {
        'q': qstr,
        'fq': filter_queries,
        'facet': 'on',
        'facet.field': facet_fields,
        'facet.limit': facet_limit,
        'facet.mincount': facet_mincount,
        'fl': ",".join(select_fields),
        'rows': rows
    }
    if json_facet:
        params['json.facet'] = json.dumps(json_facet)

    if facet_field_limits is not None:
        for (f,flim) in facet_field_limits.items():
            params["f."+f+".facet.limit"] = flim
            
    
    if len(facet_pivot_fields) > 0:
        params['facet.pivot'] = ",".join(facet_pivot_fields)
        params['facet.pivot.mincount'] = 1
    print("PARAMS="+str(params))
    results = solr.search(**params)
    fcs = results.facets

    
    payload = {
        'facet_counts': translate_facet_field(fcs),
        'pagination': {}
    }

    if include_raw:
        # note: this is not JSON serializable, do not send via REST
        payload['raw'] = results

    # TODO - check if truncated

    print("COMPACT="+str(use_compact_associations))
    if use_compact_associations:
        payload['compact_associations'] = translate_docs_compact(results.docs, field_mapping=field_mapping, **kwargs)
    else:
        payload['associations'] = translate_docs(results.docs, field_mapping=field_mapping, **kwargs)

    if 'facet_pivot' in fcs:
        payload['facet_pivot'] = fcs['facet_pivot']
    if 'facets' in results.raw_response:
        payload['facets'] = results.raw_response['facets']
    #print("FCS="+str(payload['facets']))
        
    # For solr, we implement this by finding all facets
    # TODO: no need to do 2nd query, see https://wiki.apache.org/solr/SimpleFacetParameters#Parameters
    if fetch_objects:
        core_object_field = M.OBJECT
        if slim is not None and len(slim)>0:
            core_object_field = M.OBJECT_CLOSURE
        object_field = map_field(core_object_field, field_mapping)
        if invert_subject_object:
            object_field = map_field(M.SUBJECT, field_mapping)
        oq_params = params.copy()
        oq_params['fl'] = []
        oq_params['facet.field'] = [object_field]
        oq_params['facet.limit'] = -1
        oq_params['rows'] = 0
        oq_params['facet.mincount'] = 1
        oq_results = solr.search(**oq_params)
        ff = oq_results.facets['facet_fields']
        ofl = ff.get(object_field)
        # solr returns facets counts as list, every 2nd element is number, we don't need the numbers here
        payload['objects'] = ofl[0::2]
        
    if slim is not None and len(slim)>0:
        if 'objects' in payload:
            payload['objects'] = [x for x in payload['objects'] if x in slim]
        for a in payload['associations']:
            a['slim'] = [x for x in a['object_closure'] if x in slim]
            del a['object_closure']
        
    
    return payload

def solr_quotify(v):
    if isinstance(v, list):
        return '({})'.format(" OR ".join([solr_quotify(x) for x in v]))
    else:
        # TODO - escape quotes
        return '"{}"'.format(v)

def translate_facet_field(fcs):
    """
    Translates solr facet_fields results into something easier to manipulate

    A solr facet field looks like this: [field1, count1, field2, count2, ..., fieldN, countN]

    We translate this to a dict {f1: c1, ..., fn: cn}

    This has slightly higher overhead for sending over the wire, but is easier to use
    """
    ffs = fcs['facet_fields']
    rs={}
    for (facet, facetresults) in ffs.items():
        pairs = {}
        rs[facet] = pairs
        for i in range(int(len(facetresults)/2)):
            (fv,fc) = (facetresults[i*2],facetresults[i*2+1])
            pairs[fv] = fc
    return rs

def select_distinct(distinct_field=None, **kwargs):
    """
    select distinct values for a given field for a given a query
    """
    results = search_associations(rows=0,
                                  select_fields=[],
                                  facet_field_limits = {
                                      distinct_field : -1
                                  },
                                  facet_fields=[distinct_field],
                                  **kwargs
    )
    return list(results['facet_counts'][distinct_field].keys())

        
def select_distinct_subjects(**kwargs):
    """
    select distinct subject IDs given a query
    """
    return select_distinct(M.SUBJECT, **kwargs)



def calculate_information_content(**kwargs):
    """

    Arguments are as for search_associations, in particular:

     - subject_category
     - object_category
     - subject_taxon

    """
    # TODO - constraint using category and species
    results = search_associations(rows=0,
                                  select_fields=[],
                                  facet_field_limits = {
                                      M.OBJECT : -1
                                  },
                                  facet_fields=[M.OBJECT],
                                  **kwargs
    )
    pop_size = None
    icmap = {}

    # find max
    for (f,fc) in results['facet_counts'][M.OBJECT].items():
        if pop_size is None or pop_size < fc:
            pop_size = fc

    # IC = -Log2(freq)
    for (f,fc) in results['facet_counts'][M.OBJECT].items():
        freq = fc/pop_size
        icmap[f] = -math.log(freq, 2)
    return icmap

    

# GO-SPECIFIC CODE

def goassoc_fieldmap():
    """
    Returns a mapping of canonical monarch fields to amigo-golr.

    See: https://github.com/geneontology/amigo/blob/master/metadata/ann-config.yaml
    
    """
    return {
        M.SUBJECT: 'bioentity',
        M.SUBJECT_CLOSURE: 'bioentity',
        M.SUBJECT_LABEL: 'bioentity_label',
        M.SUBJECT_TAXON: 'taxon',
        M.SUBJECT_TAXON_LABEL: 'taxon_label',
        M.OBJECT: 'annotation_class',
        M.OBJECT_CLOSURE: 'isa_partof_closure',
        M.OBJECT_LABEL: 'annotation_class_label',
        M.SUBJECT_CATEGORY: None,
        M.OBJECT_CATEGORY: None,
        M.IS_DEFINED_BY: 'assigned_by'
    }

def map_field(fn, m) :
    """
    Maps a field name, given a mapping file.
    Returns input if fieldname is unmapped.
    """
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
    """
    Perform association search using Monarch golr
    """
    go_golr_url = "http://golr.geneontology.org/solr/"
    go_solr = pysolr.Solr(go_golr_url, timeout=5)
    return search_associations(subject_category,
                               object_category,
                               relation,
                               subject,
                               solr=go_solr,
                               field_mapping=goassoc_fieldmap(),
                               **kwargs)
