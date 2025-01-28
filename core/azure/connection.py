# core/azure/connection.py
import configparser
import os
from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication

def connect_to_azure():
    """
    Устанавливает соединение с Azure DevOps.
    """
    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.dirname(__file__), '../../config/settings.ini'))

    org_url = config['AZURE_DEVOPS']['ORG_URL']
    access_token = config['AZURE_DEVOPS']['ACCESS_TOKEN']

    credentials = BasicAuthentication('', access_token)
    return Connection(base_url=org_url.rstrip('/') + '/', creds=credentials)
