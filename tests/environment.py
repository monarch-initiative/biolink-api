#### ADAPTED FROM MONARCH

import os
import time

###
### Simple (but somewhat excessive for the data parts) environment.
###

## Run this before anything else.
def before_all(context):
    ## Determine the server target. Default: http://beta.monarchinitiative.org.
    context.target = 'http://api.monarchinitiative.org/api'
    context.content_type = None
    
## Do this after completing everything.
def after_all(context):
    pass

