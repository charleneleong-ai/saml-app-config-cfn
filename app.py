#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import argparse
import xml.etree.ElementTree as ET


# from src.cfn_deploy import (
    
# )

module_path = os.path.dirname(os.path.realpath(__file__))


def main(args):
    print(args)
    metadata_file = args.metadata
    if metadata_file[-4]!='.xml':
        with open(metadata_file, encoding='utf-8') as f:
            text=f.read().replace(' ', '').replace('\n', '').replace('"', '\\"')
            
    else:
        print(f'There was a problem processing {metadata_file}. Please check file format is *.xml.')





    

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create SAML roles for External AWS accounts')
    parser.add_argument('--metadata', '--metadata-file', required=True, metavar='Metadata filename', help='The name of the metadata XML file')
    parser.add_argument('--saml', '--saml-provider-name', metavar='SAML provider name', help='The name of the SAML provider')
    parser.add_argument('--app', '--app-name', metavar='Application name', help='The name of the application required for federated access')
    
    args = parser.parse_args()
    main(args)
