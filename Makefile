SERVER= http://api.monarchinitiative.org/api
SERVER_DEV= http://localhost:5000/api
SWAGGER= $(SERVER)/swagger.json

test: behave-tests subpackage_tests

behave-tests:
	cd tests && behave

clients: biolink-javascript-client

biolink-%-client:
	swagger-codegen generate -i $(SWAGGER) -l $* -o $@

datamodel: biomodel/core.py

swagger.json:
	wget $(SWAGGER) -O $@

biomodel/core.py: ./biolink/datamodel/serializers.py
	./util/gen-class-model.pl $< > $@.tmp && mv $@.tmp $@

biomodel/obograph.py: ./biolink/datamodel/obograph_serializers.py
	./util/gen-class-model.pl $< > $@.tmp && mv $@.tmp $@

EXAMPLE-QUERIES.md:
	./util/behave-to-markdown.pl tests/*.feature > $@

PACKAGES = prefixcommons scigraph biogolr
subpackage_tests: $(patsubst %,test-%,$(PACKAGES))

test-%:
	pytest $*/tests/*.py
