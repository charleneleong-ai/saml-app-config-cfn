
This code for [`saml_provider_creator.py`](saml_provider_creator.py) is just here for reference, however it is small enough to be defined inline in the CloudFormation template [`saml-app-config.yml`](../templates/saml-app-config.yml).



Please use the [`xml_to_params.sh`](./xml_to_params.sh) script to generate `params.json` which will transform the XML metadata file to single-line JSON format to create the SamlIdentityProvider. This functionality has now been incorporated in [`app.py`](../app.py) to automate the Cloudformation deployment.