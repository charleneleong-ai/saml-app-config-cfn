#!/usr/bin/env bash


METADATA_FILE=$1

if [ -z "$1" ]
  then
    echo 'No metadata file supplied.'
    exit
fi


# Replaces '\n' with space
# Strips whitespace 
# JQ replaces " with \" to be JSON readable
if [ ${METADATA_FILE: -4} == '.xml' ]
then
    OUT_XML="$(tr '\n' ' ' < $METADATA_FILE | sed -e 's/>[ \t]*</></g' )"
    
    jq -n --arg xml "$OUT_XML" '[{ParameterKey: "MetadataDocument", ParameterValue: $xml}]' > params.json

    echo "${METADATA_FILE} successfully processed to params.json"
else
    echo "There was a problem processing ${METADATA_FILE}. Please check file format is *.xml."
fi



