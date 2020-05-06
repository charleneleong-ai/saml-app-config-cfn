#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
import argparse
import json
import boto3
import botocore
import logging
import string
from cfn_tools import load_yaml, dump_yaml
# from awsume.awsumepy import awsume

logging.basicConfig(level=os.environ.get('LOGLEVEL', 'INFO'))

cfn = boto3.client('cloudformation')

module_path = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_PATH = os.path.join(module_path, 'templates', 'saml-app-config.yml')


def main(args):
    if os.path.isdir(args.metadata_filepath):
        for metadata_file in args.metadata_filepath:
            # s = awsume(aws_profile)
            # cfn = s.client('cloudformation', region_name='ap-southeast-2')
            args.metadata_filepath = metadata_file
            account_profile =  metadata_file.split('/')[-1].replace('.xml', '')
            params = build_params(args)
            cfn_deploy(args.stack_name, params, account_profile)
            cfn_delete(args.stack_name)
    else:
        account_profile =  args.metadata_filepath.split('/')[-1].replace('.xml', '')
        params = build_params(args)
        cfn_deploy(args.stack_name, params, account_profile)
        cfn_delete(args.stack_name)


def build_params(args):
    metadata_text = _parse_metadata_file(args.metadata_filepath)
    template_data = _parse_template_file(args.template)
    if args.params_file:
        parameter_data = _parse_params_file(args.params_file)
    else:
        parameter_data = _create_params_list(args)

    parameter_data = _append_metadata_param(parameter_data, metadata_text)
    parameter_data = _validate_parameter_data(args.template, parameter_data)
    with open('params.json', 'w') as outfile:
        json.dump(parameter_data, outfile, indent=2)    
    
    params = {
        'StackName': args.stack_name,
        'TemplateBody': template_data,
        'Parameters': parameter_data,
        'Capabilities': ['CAPABILITY_NAMED_IAM']
    }
    return params
 
 
def cfn_deploy(stack_name, params, account_profile): 
    '''aws cloudformation deploy (create or update)'''
    try:
        if _stack_exists(stack_name):
            print(f'Updating the CloudFormation stack {stack_name} ...')
            stack_result = cfn.update_stack(**params)
            waiter = cfn.get_waiter('stack_update_complete')
        else:
            print(f'Creating CloudFormation stack {stack_name} ...')
            stack_result = cfn.create_stack(**params)
            waiter = cfn.get_waiter('stack_create_complete')   
        print('...waiting for stack to be ready...')
        waiter.wait(StackName=stack_name)
    except botocore.exceptions.ClientError as e:
        error_message = e.response['Error']['Message']
        if error_message == 'No updates are to be performed.':
            print("\nNo changes detected in CloudFormation stack.")
        else:
            raise
    else:
        print(f'\nSuccessfully deployed {stack_name}')
        outputs = cfn.describe_stacks(StackName=stack_result['StackId'])['Stacks'][0]['Outputs']
        SAMLProviderARN = outputs[0]['OutputValue']
        SamlFederatedAdministratorAccessRoleArn = outputs[1]['OutputValue']
        print(json.dumps(cfn.describe_stacks(StackName=stack_result['StackId']),
                indent=2, default=str))
        print(f'\nPlease paste this into Attribute Mappings in the SSO Application {account_profile} to create the SAML assertion')
        print(f'\nUser Attribute\n-----------\nhttps://aws.amazon.com/SAML/Attributes/Role')
        print(f'\n{SAMLProviderARN},{SamlFederatedAdministratorAccessRoleArn}')


def cfn_delete(stack_name):
    cfn.delete_stack(StackName=stack_name)
    print(f'\nCleaning up resources for {stack_name}...')


def _validate_parameter_data(template, parameter_data):
    '''Drops keys not in CFN template'''
    text = open(template).read()
    template_data = load_yaml(text)
    template_parameters = list(template_data['Parameters'].keys())
    for param in parameter_data:
        if param['ParameterKey'] not in template_parameters:
            parameter_data.remove(param)
            print(f"Removed {param['ParameterKey']} from params")
    return parameter_data


def _parse_template_file(template):
    with open(template) as template_fileobj:
        template_data = template_fileobj.read()
    cfn.validate_template(TemplateBody=template_data)
    return template_data


def _parse_params_file(parameters):
    with open(parameters) as parameter_fileobj:
        parameter_data = json.load(parameter_fileobj)
    return parameter_data


def _parse_metadata_file(metadata_file):
    if metadata_file[-4] != '.xml':
        with open(metadata_file, 'r', encoding='utf-8') as f:
            return f.read().replace('\n', '')
    else:
        print(f'There was a problem processing {metadata_file}. Please check file format is *.xml.')


def _create_params_list(args):
    parameter_data = []
    for arg in vars(args):
        if getattr(args, arg) == None: continue
        param_key = string.capwords(arg.replace('_', ' ')).replace(' ', '')
        param =  {"ParameterKey": param_key}
        param['ParameterValue'] = getattr(args, arg)
        parameter_data.append(param)
    return parameter_data



def _append_metadata_param(parameter_data, metadata_text):
    metadata_param = {"ParameterKey": "MetadataFile"}
    metadata_param['ParameterValue'] = metadata_text
    parameter_data.append(metadata_param)
    return parameter_data



def _stack_exists(stack_name):
    paginator = cfn.get_paginator('list_stacks')
    for page in paginator.paginate():
        for stack in page['StackSummaries']:
            if stack['StackStatus'] == 'DELETE_COMPLETE':
                continue
            if stack['StackName'] == stack_name:
                return True
    return False




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create SAML roles for External AWS accounts')
    parser.add_argument('--metadata-filepath', metavar='Metadata file path',
                        help='The name of the metadata XML file')
    parser.add_argument('--stack-name', metavar='CloudFormation Stack Name', default='saml-app-config',
                        help='The name of the metadata XML file')
    parser.add_argument('--saml-provider-name', metavar='SAML provider name', default='SamlProviderName',
                        help='The name of the SAML provider')
    parser.add_argument('--saml-app', metavar='Application name', default='AppName',
                        help='The name of the application required for federated access')
    parser.add_argument('--template', metavar='CloudFormation Template path', default=TEMPLATE_PATH,
                        help='The path to CloudFormation template path')
    parser.add_argument('--params-file', metavar='Parameters file path', help='The parameter file')

    args = parser.parse_args()
    main(args)