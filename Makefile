VERSION ?= 3.6
RUNTIME ?= python

build:
	docker build \
		--target base \
		--build-arg VERSION=$(VERSION) \
		-t 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION) \
		-f $(RUNTIME)/$(VERSION)/Dockerfile .

build-test:
	docker build \
		--target test \
		--build-arg VERSION=$(VERSION) \
		-t 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION)-test \
		-f $(RUNTIME)/$(VERSION)/Dockerfile .

push:
	docker push 3mcloud/lambda-packager:$(RUNTIME)-$(VERSION)

publish: build push

develop: build-test
	docker run -it --rm \
		-w / \
		-v ${PWD}/$(RUNTIME)/$(VERSION):/src \
		-v ${PWD}/tests/$(RUNTIME)/$(VERSION):/tests \
		3mcloud/lambda-packager:$(RUNTIME)-$(VERSION)-test

test: build-test
	# rm -rf ${PWD}/tests/$(RUNTIME)/$(VERSION)/deployment.zip
	docker run -it --rm \
		-w / \
		-v ${PWD}/tests/$(RUNTIME)/$(VERSION):/tests \
		3mcloud/lambda-packager:$(RUNTIME)-$(VERSION)-test \
		python3 -m pytest -v \
			-W ignore::DeprecationWarning \
			--cov-report term-missing \
			--cov=entrypoint.py \
			--cov-fail-under=80 \
			tests


