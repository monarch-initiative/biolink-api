from flask_restplus import fields
from biolink.api.restplus import api


node = api.model('Node', {
    'id': fields.String(readOnly=True, description='ID or CURIE e.g. MGI:1201606', required=True),
    'label': fields.String(readOnly=True, description='RDFS Label'),
})


# Schema for posting to /sim/score
features = api.model('Feature', {
    'id': fields.String(description='curie formatted id'),
    'label': fields.String(description='curie formatted id'),
    'type': fields.String(description='feature type (only phenotype supported)'),
    'isPresent': fields.Boolean(description='is the feature present')
})

sufficiency_input = api.model('SufficiencyPostInput', {
    'id': fields.String(description='curie formatted id'),
    'features': fields.List(fields.Nested(features), description='list of features')
})

# Schema for output document for annotation sufficiency
sufficiency_output = api.model('SufficiencyOutput', {
    'simple_score': fields.Float(description='simple score'),
    'scaled_score': fields.Float(description='scaled score'),
    'categorical_score': fields.Float(description='categorical score'),
})


# Schema for posting to /sim/compare
compare_input = api.model('CompareInput', {
    'reference_ids': fields.List(
        fields.String(description='curie formatted id'),
        description='list of ids'
    ),
    'query_ids': fields.List(fields.List(
            fields.String(description='curie formatted id'),
            description='list of ids'
        ),
        description='list of query profiles'
    )
})

# Schema for output document for sim search

ic_node = api.inherit('IcNode', node, {
    'IC': fields.Float(description='Information content'),
})

typed_node = api.inherit('TypedNode', node, {
    'type': fields.String(description='node type (eg phenotype, disease)'),
    'taxon': fields.Nested(node, description='taxon')
})

pairwise_match = api.model('PairwiseMatch', {
    'reference': fields.Nested(ic_node, description='reference id'),
    'match': fields.Nested(ic_node, description='match id'),
    'lcs': fields.Nested(ic_node, description='lowest common subsumer')
})

sim_match = api.inherit('SimMatch', typed_node, {
    'rank': fields.String(description='rank'),
    'score': fields.Float(description='sim score'),
    'significance': fields.String(description='p-value'),
    'pairwise_match': fields.List(fields.Nested(pairwise_match, description='list of pairwise matches'))
})

sim_query = api.model('SimQuery', {
    'ids': fields.List(fields.Nested(node, description='list of ids')),
    'negated_ids': fields.List(fields.Nested(node, description='list of ids')),
    'unresolved_ids': fields.List(fields.String(description='curie formatted id'),
                                  description='list of unresolved ids'),
    'target_ids': fields.List(fields.List(fields.Nested(node, description='query ids'))),
    'reference': fields.Nested(typed_node,
                               description="reference individual or class (eg gene, disease)")
})

sim_metadata = api.model('SimMetadata', {
    'max_max_ic': fields.Float(description='max IC')
})

sim_result = api.model('SimResult', {
    'query': fields.Nested(sim_query),
    'matches': fields.List(fields.Nested(sim_match, description='list of matches')),
    'metadata': fields.Nested(sim_metadata)
})
