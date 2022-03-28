import logging

from hargreaves.config.loader import ConfigLoader

logging.getLogger(__name__).addHandler(logging.NullHandler())


def load_api_config(api_secrets_filename=None):
    return ConfigLoader().load_api_config(api_secrets_filename=api_secrets_filename)
