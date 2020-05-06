#!/usr/bin/env python3
# -*- coding:utf-8 -*-

import boto3
from botocore.exceptions import ClientError
import json
import cfnresponse

iam = boto3.client("iam")

def create_provider(name, doc):
    try:
        resp = iam.create_saml_provider(SAMLMetadataDocument=doc, Name=name)
        return(True, resp['SAMLProviderArn'])
    except Exception as e:
        return (False, f"Cannot create SAML provider: {e}")


def delete_provider(arn):
    try:
        resp = iam.delete_saml_provider(SAMLProviderArn=arn)
        return (True, f"SAML provider with ARN {arn} deleted")
    except ClientError as e:
        if e.response['Error']['Code'] == "NoSuchEntity":
            # no need to delete a thing that doesn't exist
            return (True, f"SAML provider with ARN {arn} does not exist, deletion succeeded")
        else:
            return (False, f"Cannot delete SAML provider with ARN {arn}: {e}")
    except Exception as e:
        return (False, f"Cannot delete SAML provider with ARN {arn}: {e}")


def update_provider(name, arn, doc):
        # Need to create the ARN from the name
    arn = f"arn:aws:iam::${AWS::AccountId}:saml-provider/{name}"
    try:
        resp = iam.update_saml_provider(
            SAMLMetadataDocument=doc, SAMLProviderArn=arn)
        return (True, f"SAML provider {arn} updated")
    except Exception as e:
        return (False, f"Cannot update SAML provider {arn}: {e}")


def lambda_handler(event, context):
    provider_xml = event['ResourceProperties']['Metadata']
    provider_name = event['ResourceProperties']['Name']
    # create a default ARN from the name; will be overwritten if we are creating
    provider_arn = f"arn:aws:iam::${AWS::AccountId}:saml-provider/{provider_name}"

    if event['RequestType'] == 'Create':
        res, provider_arn = create_provider(provider_name, provider_xml)
        reason = "Creation succeeded"
    elif event['RequestType'] == 'Update':
        res, reason = update_provider(provider_name, provider_arn, provider_xml)
    elif event['RequestType'] == 'Delete':
        res, reason = delete_provider(provider_arn)
    else:
        res = False
        resp = "Unknown operation: " + event['RequestType']

    responseData = {}
    responseData['Reason'] = reason
    if res:
        cfnresponse.send(event, context, cfnresponse.SUCCESS,
                         responseData, provider_arn)
    else:
        cfnresponse.send(event, context, cfnresponse.FAILED,
                         responseData, provider_arn)
