import config
import exceptions
import utils

import logging
import requests
import time
from typing import Callable, Optional


class Session:
    """Contains basic functionality to interact with Oracle Responsys API."""

    def __init__(
        self,
        login_base_url: str = config.LOGIN_BASE_URL,
        base_resource_path: str = config.BASE_RESOURCE_PATH
    ) -> None:
        """Initialized with the API login base URL and base resource path.

        Parameters
        ----------
            login_base_url : str
                The base URL used for authentication.
            base_resource_path : str
                The base resource path used for most of the API calls.
        """
        self._login_base_url: str = login_base_url
        self._base_resource_path: str = base_resource_path
        self._last_login_response: dict = {}
        self._auth_token: str = ""
        self._obtained_url: str = ""

    # Getters
    @property
    def last_login_response(self):
        """Stored authentication response."""
        return self._last_login_response

    def get_last_login_response(self):
        """Stored authentication response."""
        return self._last_login_response

    @property
    def auth_token(self):
        """Token needed for most of the Responsys API requests."""
        return self._auth_token

    def get_auth_token(self):
        """Token needed for most of the Responsys API requests."""
        return self._auth_token

    # Authentication
    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Logging in with the username and password"
    )
    def password_login(
        self,
        user_name: str,
        password: str
    ) -> None:
        """Retrieves and sets the auth token and endpoint for the session.

        Member functions of the Session instance will automatically use the
        generated auth token.

        "The very first REST API request must be to authenticate to a specific
        Responsys account. Upon successful authentication, a token and an
        endpoint are returned in the response. You must use these authToken and
        endPoint values for any subsequent REST API request."

        Parameters
        ----------
            user_name : str
            password : str
        """
        resource_path: str = self._base_resource_path + "auth/token"
        response = self._try_request(
                function=requests.post,
                timeout=config.TRY_REQUEST_SETTINGS['request_timeout'],
                url=self._login_base_url+resource_path,
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                data={
                    'user_name': user_name,
                    'password': password,
                    'auth_type': 'password'
                }
        )
        self._set_last_login_response(response)
        self._set_auth_token()
        self._set_obtained_url()

    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Refreshing auth token"
    )
    def refresh_token(self) -> None:
        """Refreshes the auth token with the already existing token.

        "In the REST API, the authorization token is stateless, and it always
        expires after two hours. However, you can refresh the existing token
        before it expires. If you refresh the token, the system generates a new
        token from the existing valid one, so that you will not need to
        re-authenticate. The same token used previously is not returned."
        """
        resource_path: str = self._base_resource_path + "auth/token"
        response = self._try_request(
            function=requests.post,
            timeout=config.TRY_REQUEST_SETTINGS['request_timeout'],
            url=self._login_base_url+resource_path,
            headers={'Authorization': self._auth_token},
            data={'auth_type': 'token'}
        )
        self._set_last_login_response(response)
        self._set_auth_token()
        self._set_obtained_url()

    # API Throttle
    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Retrieving Responsys API throttle limits"
    )
    def get_throttle_limits(self) -> dict:
        """Obtains a list of API throttling limits for your Responsys account.

        "Responsys monitors and throttles the frequency of API requests that
        are submitted from each Oracle Responsys account. This is to ensure
        that the best possible level of service is offered to API clients in a
        shared environment."

        Returns
        -------
            dict
        """
        resource_path: str = "/rest/api/ratelimit"
        response = self._try_request(
            function=requests.get,
            timeout=config.TRY_REQUEST_SETTINGS['request_timeout'],
            url=self._obtained_url+resource_path,
            headers={'Authorization': self._auth_token}
        )
        return response.json()

    # Campaigns
    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Fetching a campaign"
    )
    def fetch_a_campaign(self, campaign_name: str) -> dict:
        """Fetches the campaign object and its properties.

        "Campaign object includes the campaign ID and the campaign's other
        properties. The links array contains the campaign object's related API
        operations, specific to the campaign name where applicable."

        Parameters
        ----------
            campaign_name : str

        Returns
        -------
            dict
        """
        resource_path: str = self._base_resource_path + "campaigns/" +  \
            campaign_name
        response = self._try_request(
            function=requests.get,
            timeout=config.TRY_REQUEST_SETTINGS['request_timeout'],
            url=self._obtained_url+resource_path,
            headers={
                'Authorization': self._auth_token,
                'Content-Type': 'application/json'
            }
        )
        return response.json()

    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Fetching a batch of campaigns"
    )
    def fetch_all_campaigns(
        self,
        limit: int = 200, offset: int = 0, campaign_type: str = "email",
        resource_path: Optional[str] = None
    ) -> dict:
        """Fetches a maximum of 200 campaigns and their properties at a time.

        "Obtain the campaign properties for all EMD Email, Push, Message
        Center, SMS, or MMS campaigns."

        Retrieved in ascending order of campaign id.

        Parameters
        ----------
            offset : int
            limit : int
            campaign_type : str
            resource_path : str
                Optional, overrides the offset, limit, and campaign_type args.

        Returns
        -------
            dict
        """
        if resource_path is None:
            resource_path = self._base_resource_path +  \
                f"campaigns?limit={limit}&offset={offset}&type={campaign_type}"
        response = self._try_request(
            function=requests.get,
            timeout=config.TRY_REQUEST_SETTINGS['request_timeout'],
            url=self._obtained_url+resource_path,
            headers={
                'Authorization': self._auth_token,
                'Content-Type': 'application/json'
            }
        )
        return response.json()

    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Begin fetching every campaign",
        after_msg="Finished fetching every campaign"
    )
    def complete_fetch_all_campaigns(
        self, campaign_type: str = "email"
    ) -> dict:
        """Runs fetch_all_campaigns until all campaigns are fetched.

        Parameters
        ----------
            campaign_type : str

        Returns
        -------
            dict
        """
        fetched: dict = self.fetch_all_campaigns(
            limit=200, offset=0, campaign_type=campaign_type
        )
        # Get the resource_path for the next batch, if available.
        resource_path: str = self._get_next_resource_path(fetched)
        while (resource_path):
            current_batch: dict = self.fetch_all_campaigns(
                resource_path=resource_path
            )
            fetched['campaigns'] += current_batch['campaigns']
            fetched['links'] = current_batch['links']
            resource_path = self._get_next_resource_path(fetched)
        self._dedupe("campaigns", fetched)
        return fetched

    # Programs
    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Fetching a batch of programs"
    )
    def fetch_all_programs(
        self,
        limit: int = 200, offset: int = 0, status: str = "",
        resource_path: Optional[str] = None
    ) -> dict:
        """Fetches a maximum of 200 programs and their properties at a time.

        "Use this interface to get a list of Responsys program orchestrations
        for an account and the associated metadata for each program. The
        response includes draft and published programs, and it includes program
        status information."

        Retrieved in ascending order of program id.

        Parameters
        ----------
            limit : int
            offset : int
            status : str
            resource_path : str
                Optional, overrides the offset, limit, and status args.

        Returns
        -------
            dict
        """
        if resource_path is None:
            resource_path = self._base_resource_path +  \
                f"programs?limit={limit}&offset={offset}&status={status}"
        response = self._try_request(
            function=requests.get,
            timeout=config.TRY_REQUEST_SETTINGS['request_timeout'],
            url=self._obtained_url+resource_path,
            headers={
                'Authorization': self._auth_token,
                'Content-Type': 'application/json'
            }
        )
        return response.json()

    @utils.log_wrap(
        logging_func=logging.info,
        before_msg="Begin fetching every program",
        after_msg="Finished fetching every program"
    )
    def complete_fetch_all_programs(self, status: str = "") -> dict:
        """Runs fetch_all_programs until all programs are fetched.

        Parameters
        ----------
            status : str

        Returns
        -------
            dict
        """
        fetched: dict = self.fetch_all_programs(
            limit=200, offset=0, status=status
        )
        # Get the resource_path for the next batch, if available.
        resource_path: str = self._get_next_resource_path(fetched)
        while (resource_path):
            current_batch: dict = self.fetch_all_programs(
                resource_path=resource_path
            )
            fetched['programs'] += current_batch['programs']
            fetched['links'] = current_batch['links']
            resource_path = self._get_next_resource_path(fetched)
        self._dedupe("programs", fetched)
        return fetched

    # Private member functions
    @utils.log_wrap(
        logging_func=logging.debug,
        before_msg="Setting the last login response"
    )
    def _set_last_login_response(self, response: requests.Response) -> None:
        """Sets and saves the last login response.

        Parameters
        ----------
            response : requests.Response
        """
        self._last_login_response = response.json()

    @utils.log_wrap(
        logging_func=logging.debug,
        before_msg="Setting the auth token"
    )
    def _set_auth_token(self) -> None:
        """Sets the auth token needed for most of the other API calls."""
        self._auth_token = self._last_login_response['authToken']

    @utils.log_wrap(
        logging_func=logging.debug,
        before_msg="Setting the obtained URL"
    )
    def _set_obtained_url(self) -> None:
        """Sets the obtained URL needed for most of the other API calls."""
        self._obtained_url = self._last_login_response['endPoint']

    @utils.log_wrap(
        logging_func=logging.debug,
        before_msg="Trying request"
    )
    def _try_request(
        self,
        function: Callable,
        settings: dict = config.TRY_REQUEST_SETTINGS,
        *args,
        **kwargs
    ) -> requests.Response:
        """Attempts the passed function a specified number of times.

        Non-zero exit status returned after the last attempt.

        Parameters
        ----------
            settings : dict
                times_to_try : int
                    Number of attempts made for an API call before giving up.
                wait_before_next_attempt : float
                    Amount of time in seconds to wait between each attempt.
                target_status_codes : list
                    Try an API call until this status code is returned.
            function : func
                Pointer to the request function.
            *args
                Variable length argument list for the passed function.
            **kwargs
                Keyword arguments for the passed function.
        Returns:
        --------
            response (requests.Response)
        """
        for i in range(settings['times_to_try']):
            try:
                response = function(
                    *args, **kwargs
                )
                if response.status_code not in settings['target_status_codes']:
                    logging.warning(
                        "Targeted status code was not returned. "
                        f"Response status code == {response.status_code}. "
                        f"Attempts so far: {i+1}"
                    )
                else:
                    return response
            except requests.exceptions.HTTPError:
                logging.warning(
                    f"Unsuccessful status code {response.status_code} was"
                    f"returned. Attempts so far: {i+1}"
                )
            except requests.exceptions.Timeout:
                logging.warning(
                    f"Request timed out. Attempts so far: {i+1}"
                )
            except requests.exceptions.ConnectionError:
                logging.warning(
                    f"Connection error encountered. Attempts so far: {i+1}"
                )
            except requests.exceptions.TooManyRedirects:
                logging.warning(
                    f"Request exceeded the configured number of maximum "
                    f"redirections. Attempts so far: {i+1}"
                )
            if i+1 != config.TRY_REQUEST_SETTINGS['times_to_try']:
                logging.warning(
                    "Retrying in {} seconds...".format(
                        config.TRY_REQUEST_SETTINGS['wait_before_next_attempt']
                    )
                )
                time.sleep(
                    config.TRY_REQUEST_SETTINGS['wait_before_next_attempt']
                )
        logging.critical(
            f"Failed request {settings['times_to_try']} times, exiting "
            "program."
        )
        raise exceptions.FailedTryRequest()

    @utils.log_wrap(
        logging_func=logging.debug,
        before_msg="Getting the resource path for the next batch, if available"
    )
    def _get_next_resource_path(self, fetched: dict) -> str:
        """Retrieves next href value from results of a complete fetch all.

        Parameters
        ----------
            fetched : dict

        Returns
        -------
            str
        """
        resource_path: str = ""
        for link in fetched['links']:
            if 'rel' in link and 'next' == link['rel']:
                resource_path = link['href']
                break
        return resource_path

    @utils.log_wrap(
        logging_func=logging.debug,
        before_msg="Deduping"
    )
    def _dedupe(self, object_type: str, fetched: dict) -> None:
        """Drops any duplicate fetched campaigns or programs.

        Parameters
        ----------
            object_type : str
                The options are "campaigns" or "programs".
            fetched : dict
        """
        fetched[object_type] = list(
            {
                object['id']: object
                for object in fetched[object_type]
            }.values()
        )
