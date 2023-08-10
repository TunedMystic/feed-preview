PROJECT=`basename $$PWD`
APP=app


# -------------------------------------------------------------------
# App-related commands
# -------------------------------------------------------------------

## @(app) - Run the app                 ⭐️
start:
	@echo "✨📦✨ Running application\n"
	@docker-compose up ${APP}


## @(app) - Run tailwindcss --watch     ⭐️
css: bin/tailwind
	@echo "✨📦✨ Running tailwind (--watch)\n"
	@bash -c "./bin/tailwind --input ./tailwind.input.css --output ./ui/static/css/style.css --minify --watch"


## @(app) - Deploy the app with Fly.io  🚀
deploy: clean
	@echo "✨🚀✨ Deploying application\n"
	@fly deploy



# -------------------------------------------------------------------
# Container-related commands
# -------------------------------------------------------------------

## @(containers) - List all the docker containers
ps:
	@docker ps -a --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"


## @(containers) - Build the images
build: clean
	@echo "✨📦✨ Building the ${APP} docker image\n"
	@docker-compose build ${APP}


## @(containers) - Build the images with no cache
build-no-cache: clean
	@echo "✨📦✨ Building the ${APP} docker image with no cache\n"
	@docker-compose build --no-cache ${APP}


## @(containers) - Destroy all running containers
wipe:
	@echo "✨📦✨ Destroying related containers\n"
	@docker container rm -fv $$(docker container ls -aq) 2> /dev/null || true


## @(containers) - Destroy all running containers and related images
wipeall: wipe
	@echo "✨📦✨ Destroying related images\n"
	@docker image rm -f $$(docker image ls -q "${APP}") $$(docker image ls -q --filter dangling=true) 2> /dev/null || true



# -------------------------------------------------------------------
# Development-related commands
# -------------------------------------------------------------------

## @(development) - Start a shell in the app container
shell:
	@docker exec -it ${APP} python -im app.main


## @(development) - Start a shell in a new container
shellx:
	@docker-compose run --rm ${APP} python -im app.main


## @(development) - Start a bash shell in the app container
bash:
	@docker exec -it ${APP} bash


## @(development) - Start a bash shell in a new container
bashx:
	@docker-compose run --rm ${APP} bash


## @(development) - Run linting checks
lint:
	@docker-compose run --rm ${APP} bash -c 'ruff check --select=E,F,B,I,A,N,W,C4,SIM,PTH,PL --ignore=E501,PLR2004 ${APP}'


## @(development) - Format the codebase
format:
	@docker-compose run --rm ${APP} bash -c 'ruff check --select=E,F,B,I,A,N,W,C4,SIM,PTH,PL --ignore=E501,PLR2004 --fix ${APP}'


## @(development) - Run tests
test:
	@docker-compose run --rm ${APP} python -m unittest discover --failfast --start-directory tests --pattern "test_*.py"


## @(development) - Remove cached files and dirs from workspace
clean:
	@echo "✨📦✨ Cleaning workspace\n"
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@find . -type f -name "*.DS_Store" -delete
	@rm -f .coverage coverage.xml


bin/tailwind:
	@echo "✨📦✨ Downloading tailwindcss binary\n"
	curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
	chmod +x tailwindcss-macos-arm64
	mkdir -p bin
	mv tailwindcss-macos-arm64 ./bin/tailwind
	@echo ""



# -------------------------------------------------------------------
# Self-documenting Makefile targets - https://git.io/Jg3bU
# -------------------------------------------------------------------

.DEFAULT_GOAL := help

help:
	@echo "Usage:"
	@echo "  make <target>"
	@echo ""
	@echo "Targets:"
	@awk '/^[a-zA-Z\-\_0-9]+:/ \
		{ \
			helpMessage = match(lastLine, /^## (.*)/); \
			if (helpMessage) { \
				helpCommand = substr($$1, 0, index($$1, ":")-1); \
				helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
				helpGroup = match(helpMessage, /^@([^ ]*)/); \
				if (helpGroup) { \
					helpGroup = substr(helpMessage, RSTART + 1, index(helpMessage, " ")-2); \
					helpMessage = substr(helpMessage, index(helpMessage, " ")+1); \
				} \
				printf "%s|  %-18s %s\n", \
					helpGroup, helpCommand, helpMessage; \
			} \
		} \
		{ lastLine = $$0 }' \
		$(MAKEFILE_LIST) \
	| sort -t'|' -sk1,1 \
	| awk -F '|' ' \
			{ \
			cat = $$1; \
			if (cat != lastCat || lastCat == "") { \
				if ( cat == "0" ) { \
					print "\nTargets:" \
				} else { \
					gsub("_", " ", cat); \
					printf "\n%s\n", cat; \
				} \
			} \
			print $$2 \
		} \
		{ lastCat = $$1 }'
	@echo ""
