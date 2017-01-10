####
#### Basic functions for checking external data resources.
####

from behave import *
from contextlib import closing
import requests
import json
import jsonpath_rw


###
### Helpers.
###

## The basic and critical remote collector.
## It defines:
##  context.code
##  context.content_type
##  context.content
##  context.content_length
def get_and_process(context, url):

    print("URL="+url)
    with closing(requests.get(url, stream=False)) as resp:
        context.code = resp.status_code
        context.content_type = resp.headers['content-type']
        if resp.status_code == 200:
            context.content = resp.text
            context.content_json = resp.json()

            

###
### Definitions.
###

## Collector for internal path.
@given('I collect data at path "{path}"')
def step_impl(context, path):
    full_url = context.target + path
    get_and_process(context, full_url)

## Collector for remote resource.
@given('I collect data at URL "{url}"')
def step_impl(context, url):
    get_and_process(context, url)

@then('the content type should be "{ctype}"')
def step_impl(context, ctype):
    print("TTTT="+context.content_type)
    if not context.content_type :
        ## Apparently no content type at all...
        assert True is False
    else:
        assert context.content_type == ctype

@then('the content should contain "{text}"')
def step_impl(context, text):
    if not context.content :
        ## Apparently no text at all...
        assert True is False
    else:
        assert context.content.rfind(text) != -1

## Adds:
##  context.content_json
@when('the content is converted to JSON')
def step_impl(context):
    if not context.content :
        ## Apparently no text at all...
        assert True is False
    else:
        context.content_json = json.loads(context.content)

@then('the JSON should have the top-level property "{prop}"')
def step_impl(context, prop):
    if not context.content_json :
        ## Apparently no JSON at all...
        assert True is False
    else:
        assert context.content_json.get(prop)

@then('the JSON should have a JSONPath "{jsonpath}"')
def step_impl(context, jsonpath):
    if not context.content_json :
        ## Apparently no JSON at all...
        assert True is False
    else:
        jsonpath_expr = jsonpath_rw.parse(jsonpath)
        res = jsonpath_expr.find(context.content_json)
        #assert len(res) > 0
        #print(res)
        assert res

@then('the JSON should have JSONPath "{jsonpath}" equal to "{thing}" "{value}"')
def step_impl(context, jsonpath, thing, value):
    if not context.content_json :
        ## Apparently no JSON at all...
        assert True is False
    else:
        jsonpath_expr = jsonpath_rw.parse(jsonpath)
        res = jsonpath_expr.find(context.content_json)
        if not res[0] :
            assert True is False
        else:
            if thing == "string":
                assert res[0].value == value
            elif thing == "integer":
                assert res[0].value == int(value)
            elif thing == "float":
                assert res[0].value == float(value)
            else:
                ## Not a thing we know how to deal with yet.
                assert True is False

@then('the JSON should have some JSONPath "{jsonpath}" with "{thing}" "{value}"')
def step_impl(context, jsonpath, thing, value):
    if not context.content_json :
        ## Apparently no JSON at all...
        assert True is False
    else:
        jsonpath_expr = jsonpath_rw.parse(jsonpath)
        results = jsonpath_expr.find(context.content_json)
        if (len(results)) == 0:
            assert True is False
        else:
            is_found = False
            for res in results:
                if thing == "string":
                    if res.value == value:
                        is_found = True
                elif thing == "integer":
                    if res.value == int(value):
                        is_found = True
                elif thing == "float":
                    if res.value == float(value):
                        is_found = True                        
                else:
                    ## Not a thing we know how to deal with yet.
                    assert True is False
            assert is_found is True
