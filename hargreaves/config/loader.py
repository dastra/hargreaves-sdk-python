import json
import logging
import os
from pathlib import Path

from ..config.models import ApiConfiguration

logger = logging.getLogger(__name__)


class ConfigLoader:

    def __init__(self):
        pass

    def load_api_config(self, api_secrets_filename=None):
        """
        :param str api_secrets_filename: The full path to the JSON file containing the credentials
        :return: .config.ApiConfiguration: The populated ApiConfiguration
        """
        # Get the config keys which contain the mapping between the ApiConfiguration attributes and the variable names
        # in the secrets.json file and environment variables e.g. username is username (secrets.json) and
        # HL_USERNAME (env variable)

        logger.debug(f"ConfigLoader::load_api_config(api_secrets_filename={api_secrets_filename}) - Start")

        with open(Path(__file__).parent.joinpath('config_keys.json')) as json_file:
            config_keys = json.load(json_file)

        # If there is a secrets file specified and it exists get the details from it
        if api_secrets_filename is not None and os.path.exists(api_secrets_filename) and os.path.isfile(
                api_secrets_filename):
            logger.debug(f"loading secrets file {api_secrets_filename}...")
            with open(api_secrets_filename, "r") as secrets:
                config = json.load(secrets)
        # If there is a secrets file specified and it does not exist log a warning to indicate that the specified file
        # could not be found and create an empty config
        elif api_secrets_filename is not None and (
                not os.path.exists(api_secrets_filename) or not os.path.isfile(api_secrets_filename)):
            raise ValueError(f"Provided secrets file of {api_secrets_filename} can not be found, please ensure you "
                             f"have correctly specified the full path to the file or don't provide a secrets file "
                             f"to use environment variables instead.")
        # If no secrets file is specified just create an empty config
        else:
            config = {}

        logger.debug(f"retrieve env values...")
        # Populate the values for the api configuration preferring the secrets file over the environment variables
        populated_api_config_values = {
            key: config.get(value["config"], os.getenv(value["env"], None)) for key, value in config_keys.items()
        }

        # Warn if there are any blank values
        if None in populated_api_config_values.values():
            raise ValueError("There are null values in the configuration. " +
                             " Please check the format of your secrets file or all environment variables are set")

        # Create the ApiConfiguration

        api_config = ApiConfiguration(**populated_api_config_values)
        logger.debug(f"ConfigLoader::load_api_config() - Done")

        return api_config
