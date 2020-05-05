# SAML 2.0 Application Configuration



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


## Preparing metadata

Please use the [`xml_to_params.sh`](./xml_to_params.sh) script to generate `params.json` which will transform the XML metadata file to single-line JSON format to create the SamlIdentityProvider. 

  $ xml_to_params.sh 

## Configuration

You can set the name of your identity provider via the `SamlProviderName` and `SamlApp` parameters in the stack

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
