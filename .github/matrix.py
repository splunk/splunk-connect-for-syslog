#!/usr/bin/env python3
import configparser
import argparse
from datetime import datetime
import json

def hasfeatures(features,section):
    if not features is None:
        for feature in features.split(','):
            value = section.getboolean(feature)
            if not value:
                return False
    return True

parser = argparse.ArgumentParser(description='Determine support matrix')
parser.add_argument('--unsupported', action='store_true',
                    help='include unsupported versions')
parser.add_argument('--features', type=str, default=None,
                    help='Required Features')
args = parser.parse_args()


config = configparser.ConfigParser()
config.read('deps/build/addonfactory_test_matrix_splunk/splunk_matrix.conf')
supported = []
for section in config.sections():
    props = {}
    supported_string = config[section]['SUPPORTED']
    eol = datetime.strptime(supported_string, '%Y-%m-%d').date()
    today = datetime.now().date()
    if not (args.unsupported or today<=eol):
        continue
    
    if not hasfeatures(args.features,config[section]):
        continue
    for k in config[section].keys():
        try:
            value = config[section].getboolean(k)
        except:
            value = config[section][k]
        props[k]=value
    supported.append(props)
#print(f"::set-output name=splunk-matrix::{json.dumps({'splunk': matrix})}")    
print(f"::set-output name=matrix::{json.dumps(supported)}")