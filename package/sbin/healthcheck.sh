#!/usr/bin/env bash
set -e
export SC4S_LISTEN_STATUS_PORT=${SC4S_LISTEN_STATUS_PORT:=8080}
url -s --fail http://localhost:${SC4S_LISTEN_STATUS_PORT}/healthz