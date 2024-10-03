"""Modules related to API calling and rate limiting functions."""

import logging
import os
import time
from dataclasses import dataclass

import requests

from utils import hms

logger = logging.getLogger(__name__)


def start_session() -> requests.sessions.Session:
    """Create a single request session.

    Handles rate limit within rate_limiter function.

    Returns:
        requests.sessions.Session: Session for api calls.
    """
    session = requests.Session()
    session.headers.update({"Authorization": f'Bearer {os.getenv("ACCESS_TOKEN")}'})

    def status_check(r, *args, **kwargs):
        r.raise_for_status()

    def rate_limiter(r, *args, **kwargs):
        remaining_call = int(r.headers["X-RateLimit-Remaining"])
        reset_time = int(r.headers["X-RateLimit-Reset"])

        remaining_time = int(reset_time) - int(time.time())
        remaining_time_str = hms(remaining_time)

        if remaining_call < 60:
            print("API Limit remaining:", remaining_call)
            print(f"Please wait for {remaining_time_str} before limit resets.")
            print("Slowing down API calls rate by 10 secs per call")
            time.sleep(10)

        if remaining_call < 1:
            print("API Limit remaining:", remaining_call)
            print(f"Please wait for {remaining_time_str} before limit resets.")
            raise ValueError(
                f"No more API limit, Please wait for {remaining_time_str} before limit resets."
            )

    session.hooks["response"] = [status_check, rate_limiter]
    return session


@dataclass
class APIRetriever:
    session: requests.sessions.Session

    def get_paginated_response(self, url_api: str) -> list[dict]:
        """Get all repositories from a url. Adds next page if "next" link is available.

        Args:
            url_api (str): API URL to retrieve from.

        Returns:
            list[dict]: list of repositories response.
        """
        repo_list = []
        resp = self.get_single_api_response(url_api)

        if resp:
            repo_list = resp.json()

            while "next" in resp.links.keys():
                resp = self.get_single_api_response(resp.links["next"]["url"])
                repo_list.extend(resp.json())
            return repo_list

    def get_single_api_response(self, url_api: str) -> requests.models.Response:
        """_summary_

        Args:
            url_api (str): _description_

        Returns:
            requests.models.Response: _description_
        """
        logger.info(f"Retrieving from API {url_api}")
        resp = None

        for _ in range(1, int(os.getenv("MAX_RETRY", 5)) + 1):
            try:
                resp = self.session.get(url_api, timeout=int(os.getenv("TIMEOUT", 20)))
                break
            except (
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
            ) as err:
                logger.warning(f"Server response timeout. Retrying.... {err=}")
                continue

        if resp is None:
            raise ValueError(f"There are no response from API call. {url_api}")

        return resp
