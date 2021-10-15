from ontobio.model.mme.request import MmeRequest
from ontobio.model.mme.response import MmeResponse

import marshmallow_dataclass

mme_request_marshmallow = marshmallow_dataclass.class_schema(MmeRequest)()
mme_response_marshmallow = marshmallow_dataclass.class_schema(MmeResponse)()
