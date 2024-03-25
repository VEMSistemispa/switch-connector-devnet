#!/usr/bin/env python3

import pathlib
import connexion
import os

import yaml
import requests

from swagger_server import encoder
from dotenv import load_dotenv
from connexion.resolver import RelativeResolver
from swagger_server.controllers.exception_controller import handle_device_not_handled, handle_device_timeout
from scrapli.exceptions import ScrapliConnectionNotOpened
from swagger_server.models.exceptions import DeviceNotHandled
from logging.config import dictConfig

load_dotenv()

LOGGER_CONFIGURATION_PATH = os.path.join(pathlib.Path(__file__).parents[1], 'logging.conf')
PORT = os.getenv('PORT') or 8080
MODE = os.getenv('MODE') or 'development'
LOG_LEVEL = os.getenv('LOG_LEVEL')
POSSIBLE_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']

def main():
    from waitress import serve
    from paste.translogger import TransLogger
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app = connexion.App(__name__, specification_dir='./swagger/')
    app.app.json_encoder = encoder.JSONEncoder
    app.add_api('openapi.yaml', arguments={'title': 'Switches connector API'}, 
                pythonic_params=True,
                strict_validation=True,
                validate_responses=True,
                resolver=RelativeResolver('swagger_server.controllers.default_controller'))
    app.add_error_handler(DeviceNotHandled, handle_device_not_handled)
    app.add_error_handler(ScrapliConnectionNotOpened, handle_device_timeout)
    serve(TransLogger(app, setup_console_handler=False), host="0.0.0.0", port=PORT) if MODE=='production' else app.run(port=PORT)


if __name__ == '__main__':
    with open(LOGGER_CONFIGURATION_PATH, "r") as stream:
        try:
            logger_config = yaml.safe_load(stream)
            if LOG_LEVEL is not None and LOG_LEVEL in POSSIBLE_LOG_LEVELS:
                logger_config['root']['level'] = LOG_LEVEL
            dictConfig(logger_config)
        except yaml.YAMLError:
            print("Unable to read logger configuration file")
    main()
