# SAML 2.0 Identity Provider

This CloudFormation template creates a SAML identity provider (IdP) and SAML Federated User with Administrator Access in Amazon Web Services' (AWS) Identity and Access Management (IAM) configuration.

In order to use it, you'll need:

- an AWS account
- rights within that AWS account to create, update, and delete:
    - CloudFormation stacks
    - IAM Roles and Policies
    - Lambda functions
    - Identity Providers
- a SAML Identity Provider (IdP)
- the Federation metadata (an XML document) from the Identity Provider (how to get this differs for every IdP)
- Python3.7 installed 
- AWS CLI configured - boto3 (AWS CLI Python SDK) will adopt AWS credentials 
- [awsume](https://awsu.me/) for batch deployment for many accounts with the  `~/.aws/config` configured correctly.

## Create virtualenv

  ```bash
  $ python -m venv .venv
  $ source .venv/bin/activate 
  ```

## Install dependencies

  ```bash
  $ pip install -r requirements-dev.txt
  ```

<!-- 
## Preparing metadata

Please use the [`xml_to_params.sh`](./xml_to_params.sh) script to generate `params.json` which will transform the XML metadata file to single-line JSON format to create the SamlIdentityProvider. 

  ```bash
  $ xml_to_params.sh 
  ``` -->
## Preparing metadata
The python script reads a SAML Federation metadata XML file and creates the SAML provider and the Federated User with Administrator Access.  

  ```bash
  $ python app.py --metadata-filepath <metadata>.xml --saml <SAML provider name> --app <Application name>
  ```

The stack deletes on creation resources after resources are successfully created.

## Configuration

The arguments you pass to the Python script override those in the CFN template.

## Returned Values from the Custom Resource

The `ProviderCreator` custom resource returns the ARN of the SAML provider as its physical resource ID.

You can simply `Ref` the custom resource to use the SAML provider ARN.

For example:

```yaml
...

  TrustingIdp:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Federated: !Ref IdentityProvider
            Action: sts:AssumeRoleWithSAML
            Condition:
              StringEquals:
                "SAML:aud": "https://signin.aws.amazon.com/saml"
...
```

## Updating the stack

The stack can be updated, though the only changes you can make to the Identity Provider is to change the SAML
Metadata document, in case you need to update the trust relationship.

<!-- 
```bash
$ aws cloudformation validate-template --template-body file://templates/saml-app-config.yml
$ aws cloudformation create-stack --stack-name  saml-app-configuration --template-body file://templates/saml-app-config.yml --parameters file://params.json --capabilities CAPABILITY_NAMED_IAM
$ aws cloudformation delete-stack --stack-name saml-app-configuration 
``` -->