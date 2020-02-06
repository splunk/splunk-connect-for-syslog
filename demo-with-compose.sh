#!/usr/bin/env bash
#Copyright 2019 Splunk, Inc.
#
#Use of this source code is governed by a BSD-2-clause-style
#license that can be found in the LICENSE-BSD2 file or at
#https://opensource.org/licenses/BSD-2-Clause
export SPLUNK=8.0
export SYSLOG=3.25.1

docker-compose build
docker-compose up -d splunk
docker-compose up -d sc4s
sleep 60
docker-compose up

EXIT=$0
