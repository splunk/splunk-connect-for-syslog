#!/usr/bin/env bash

            set -e

            REPORT_DIR=clair-reports
            mkdir $REPORT_DIR || true

            #DB=$(docker run -p 5432:5432 -d arminc/clair-db:latest)
            docker run -p 5432:5432 -d --rm --name db arminc/clair-db:latest
            #CLAIR=$(docker run -p 6060:6060 --link "$DB":postgres -d arminc/clair-local-scan:latest)'
            sleep 30
            docker run -p 6060:6060 --link db:postgres -d --rm --name clair arminc/clair-local-scan:latest
            #CLAIR_SCANNER=$(docker run -v /var/run/docker.sock:/var/run/docker.sock --link clair:clair --name clairscanner --rm -d ovotech/clair-scanner@sha256:53fe8e8ac63af330d2dfc63498d23d8825d07f916f7d230271176de06d12acd6 tail -f /dev/null)

            CLAIR_SCANNER=$(docker run --link clair:clair --name clairscanner --rm -d ovotech/clair-scanner@sha256:53fe8e8ac63af330d2dfc63498d23d8825d07f916f7d230271176de06d12acd6 tail -f /dev/null)

            #clair_ip=$(docker exec -it "$CLAIR" hostname -i | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')
            #scanner_ip=$(docker exec -it "$CLAIR_SCANNER" hostname -i | grep -oE '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+')

            docker cp "clair-whitelist.yml" "$CLAIR_SCANNER:/whitelist.yml"
            WHITELIST="-w /whitelist.yml"

            function scan() {
                echo Scanning $1
                local image=$1
                # replace forward-slashes and colons with underscores
                munged_image=$(echo "$image" | sed 's/\//_/g' | sed 's/:/_/g')
                sanitised_image_filename="${munged_image}.json"
                local ret=0
                #--ip "$scanner_ip" \
                #
                local docker_cmd=(docker exec -it "$CLAIR_SCANNER" clair-scanner \
                    --clair=http://clair:6060 \
                    -t "high" \
                    --report "$REPORT_DIR/$sanitised_image_filename" \
                    --log "$REPORT_DIR/log.json" --whitelist=${WHITELIST:+"-x"}
                    --reportAll=true \
                    --exit-when-no-features=false \
                    "$image")

                docker pull "$image"

                "${docker_cmd[@]}" 2>&1 || ret=$?
                if [ $ret -eq 0 ]; then
                    echo "No unapproved vulnerabilities"
                elif [ $ret -eq 1 ]; then
                    echo "Unapproved vulnerabilities found"
                    EXIT_STATUS=1
                elif [ $ret -eq 5 ]; then
                    echo "Image was not scanned, not supported."
                    EXIT_STATUS=1
                else
                    echo "Unknown clair-scanner return code $ret."
                    EXIT_STATUS=1
                fi

                docker cp "$CLAIR_SCANNER:/$sanitised_image_filename" "$REPORT_DIR/$sanitised_image_filename" || true
            }

            EXIT_STATUS=0

            scan "$IMAGE_NAME:$CIRCLE_SHA1"

            docker kill clairscanner
            docker kill clair
            docker kill db

            exit $EXIT_STATUS