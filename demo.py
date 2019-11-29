#!/usr/bin/env python3
import config
import rsys_api
import secrets

import logging
import sys


def main():
    # Set up logging.
    log_file_name = "demo.log"
    # # Truncate log file.
    # with open(log_file_name, "w") as file:
    #     file.truncate()
    # Configure logging.
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        filename=log_file_name
    )

    logging.info("BEGIN: {script_name}".format(script_name=sys.argv[0]))
    # Start new session.
    session = rsys_api.Session(
        config.LOGIN_BASE_URL, config.BASE_RESOURCE_PATH
    )
    # Get auth token.
    session.password_login(
        secrets.USER_NAME, secrets.PASSWORD
    )
    session.get_throttle_limits()
    logging.info("END: {script_name}\n".format(script_name=sys.argv[0]))


if __name__ == '__main__':
    main()
