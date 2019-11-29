#!/usr/bin/env python3
import config
import rsys_api
import secrets

import json
import logging
import sys


def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        filename="demo.log"
    )

    logging.info("BEGIN: {script_name}".format(script_name=sys.argv[0]))
    # Start new session.
    session = rsys_api.Session(
        config.LOGIN_BASE_URL, config.BASE_RESOURCE_PATH
    )
    # Authenticate.
    session.password_login(
        secrets.USER_NAME, secrets.PASSWORD
    )
    with open("throttle_limits.json", 'w') as output_file:
        # Output throttle limits into a json file within the same directory.
        json.dump(
            obj=session.get_throttle_limits(),
            indent=4,
            fp=output_file
        )
    with open("fetched_programs.json", 'w') as output_file:
        # Output information on all running programs into a json file within
        # the same directory.
        json.dump(
            obj=session.complete_fetch_all_programs(status="RUNNING"),
            indent=4,
            fp=output_file
        )
    with open("fetched_campaigns.json", 'w') as output_file:
        # Output information on all running programs into a json file within
        # the same directory.
        json.dump(
            obj=session.complete_fetch_all_campaigns(campaign_type="email"),
            indent=4,
            fp=output_file
        )
    logging.info("END: {script_name}\n".format(script_name=sys.argv[0]))


if __name__ == '__main__':
    main()
