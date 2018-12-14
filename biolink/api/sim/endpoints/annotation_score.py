from flask_restplus import Resource
from ontobio.sim.annotation_scorer import AnnotationScorer
from ontobio.sim.api.owlsim2 import OwlSim2Api
from biolink.api.restplus import api
from biolink.datamodel.sim_serializers import sufficiency_input, sufficiency_output

annotation_scorer = AnnotationScorer(OwlSim2Api())

score_get = api.parser()
score_get.add_argument('id', action='append', help='Phenotype identifier (eg HP:0004935)')
score_get.add_argument(
    'absent_id',
    default=[],
    action='append',
    help='absent phenotype (eg HP:0002828)'
)


class AnnotationScore(Resource):

    @api.expect(sufficiency_input)
    @api.marshal_with(sufficiency_output)
    def post(self):
        """
        Get annotation score
        """
        phenotypes = [feature['id'] for feature in sufficiency_input['features']
                      if feature['isPresent'] is True]
        absent_phenotypes = [feature['id'] for feature in sufficiency_input['features']
                             if feature['isPresent'] is False]

        return annotation_scorer.get_annotation_sufficiency(
            profile=phenotypes,
            negated_classes=absent_phenotypes
        )

    @api.expect(score_get)
    @api.marshal_with(sufficiency_output)
    def get(self):
        """
        Get annotation score
        """
        input_args = score_get.parse_args()

        return annotation_scorer.get_annotation_sufficiency(
            profile=input_args['id'],
            negated_classes=input_args['absent_id']
        )
