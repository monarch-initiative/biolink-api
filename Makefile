SERVER= https://api.monarchinitiative.org/api
SERVER_DEV= http://localhost:5000/api
SWAGGER= $(SERVER)/swagger.json

test: behave-tests subpackage_tests

behave-tests:
	cd tests && behave

CLIENT_LANGS = javascript java python
CLIENT_TARGETS = $(patsubst %, biolink-%-client, $(CLIENT_LANGS))

clients: $(CLIENT_TARGETS)

# generate client code for javascript, python etc
# after making this, copy to separate repo
biolink-%-client: swagger.json
	swagger-codegen generate -i $(SWAGGER) -l $* -o $@

deploy-%-client: biolink-%-client
	cp -pr $</* ../$<

deploy-clients: $(patsubst %, deploy-%-client, $(CLIENT_LANGS))

datamodel: biomodel/core.py

swagger.json:
	wget --no-check-certificate $(SWAGGER) -O $@

biomodel/core.py: ./biolink/datamodel/serializers.py
	./util/gen-class-model.pl $< > $@.tmp && mv $@.tmp $@

biomodel/obograph.py: ./biolink/datamodel/obograph_serializers.py
	./util/gen-class-model.pl $< > $@.tmp && mv $@.tmp $@

EXAMPLE-QUERIES.md:
	./util/behave-to-markdown.pl tests/*.feature > $@

#PACKAGES = prefixcommons scigraph biogolr
PACKAGES = ontobio prefixcommons
subpackage_tests: $(patsubst %,test-%,$(PACKAGES))

test-%:
	pytest $*/tests/*.py
