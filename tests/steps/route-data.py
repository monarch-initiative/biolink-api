####
#### Basic functions for checking external data resources.
####

from behave import *
from contextlib import closing
import requests
import json
import jsonpath_rw
import logging

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
@given('a path "{path}"')
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

@then('the content should not contain "{text}"')
def step_impl(context, text):
    if not context.content:
        ## Apparently no text at all...
        assert True is False
    else:
        assert context.content.rfind(text) == -1

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

@then('the JSON should have some JSONPath "{jsonpath}" of type "{thing}"')
def step_impl(context, jsonpath, thing):
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
                if type(res.value) == str and thing == "string":
                    is_found = True
                elif type(res.value) == int and thing == "number":
                    is_found = True
                elif type(res.value) == float and thing == "number":
                    is_found = True
                elif type(res.value) == True and thing == "boolean":
                    is_found = True
                elif type(res.value) == False and thing == "boolean":
                    is_found = True
                elif type(res.value) == dict and thing == "object":
                    is_found = True
                elif type(res.value) == list and thing == "array":
                    is_found = True
                elif res.value is None and thing == "null":
                    is_found = True
                else:
                    ## Not a thing we know how to deal with yet.
                    logging.error("Cannot interpret value: {}".format(res.value))
                    assert True is False
            assert is_found is True

@then('the gene "{jsonpath}" homolog ID should be the authoritative source for taxon')
def step_impl(context, jsonpath):
        if not context.content_json:
            ## Apparently no JSON at all...
            assert True is False
        else:
            json_expr = jsonpath_rw.parse(jsonpath)
            results = json_expr.find(context.content_json)
            if (len(results)) == 0:
                assert True is False
            else:
                is_okay = True
                for res in results:
                    print(str(res.value))
                    geneID = res.value['id']
                    taxon = res.value['taxon']['id']
                    print(geneID)
                    print(taxon)
                    if taxon == 'NCBITaxon:9606' and not geneID.startswith('HGNC'):
                        is_okay = False
                    elif taxon == 'NCBITaxon:10090' and not geneID.startswith('MGI'):
                        is_okay = False
                    elif taxon == 'NCBITaxon:10116' and not geneID.startswith('RGD'):
                        is_okay = False
                    # elif taxon == 'NCBITaxon:7955' and not geneID.startswith('ZFIN'):
                    #     is_okay = False
                    # TODO: commenting out because the this taxon can have ZFIN or NCBIGene as the gene CURIE prefix
                    elif taxon == 'NCBITaxon:7227' and not (geneID.startswith('FlyBase') or geneID.startswith('FB')):
                        is_okay = False
                    elif taxon == 'NCBITaxon:6239' and not (geneID.startswith('WormBase') or geneID.startswith('WB')):
                        is_okay = False
                    elif (taxon == 'NCBITaxon:4932' or taxon == 'NCBITaxon:559292') and not geneID.startswith('SGD'):
                        is_okay = False
                assert is_okay is True

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

@then('the JSON should have JSONPath "{jsonpath}" greater than "{thing}" "{value}"')
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
            if thing == "integer":
                assert res[0].value > int(value)
            elif thing == "float":
                assert res[0].value > float(value)
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
                elif thing == "boolean":
                    if res.value == bool(value):
                        is_found = True
                elif thing == "float":
                    if res.value == float(value):
                        is_found = True
                else:
                    ## Not a thing we know how to deal with yet.
                    logging.error("Cannot interpret: {}".format(thing))
                    assert True is False
            assert is_found is True


@then('the JSON should not have some JSONPath "{jsonpath}" with "{thing}" "{value}"')
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
                elif thing == "boolean":
                    if res.value == bool(value):
                        is_found = True
                elif thing == "float":
                    if res.value == float(value):
                        is_found = True
                else:
                    ## Not a thing we know how to deal with yet.
                    logging.error("Cannot interpret: {}".format(thing))
                    assert True is False
            assert is_found is False

@then('the JSON should have some JSONPath "{jsonpath}" containing "{thing}" "{value}"')
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
                if res.value is None or res.value=='None':
                    continue
                if thing == "string":
                    if str(value) in res.value:
                        is_found = True
                elif thing == "integer":
                    if int(value) in res.value:
                        is_found = True
                elif thing == "boolean":
                    if bool(value) in res.value:
                        is_found = True
                elif thing == "float":
                    if float(value) in res.value:
                        is_found = True
                else:
                    ## Not a thing we know how to deal with yet.
                    logging.error("Cannot interpret: {}".format(thing))
                    assert True is False
            assert is_found is True
