import argparse
import logging
import pprint
import sys

import requests
from dotenv import load_dotenv

from api_retriever import APIRetriever, start_session
from data_analyzer import DataAnalyzer
from data_model import ResponseData
from utils import setup_logging

logger = logging.getLogger(__name__)
load_dotenv()
setup_logging()

BASE_API = "https://api.github.com"


def parse_args():
    """Parse command-line arguments to retrieve organization name."""
    parser = argparse.ArgumentParser(
        description="Retrieve GitHub organization's repositories."
    )
    parser.add_argument(
        "org",
        type=str,
        nargs="?",
        default="",
        help="Name of organization to retrieve repositories name (e.g., fastapi, google)",
    )
    return parser.parse_args()


def main():
    """Main function to retrieve organization's repositories data."""
    args = parse_args()
    organization = args.org

    if not organization:
        print("Organization Params is blank. Please input the organization")
        organization = input(
            "Enter organization to retrieve repositories. e.g google: "
        )

    REPO_API = f"{BASE_API}/orgs/{organization}/repos?page=1&per_page=100"

    logger.info(f"Connecting to {organization} GitHub repositories")
    session = start_session()

    try:
        api_retriever = APIRetriever(session)
        repo_list = api_retriever.get_paginated_response(REPO_API)
        repositories = [ResponseData(**repo) for repo in repo_list]

        logger.info("Analyzing repository data.")

        data_analyzer = DataAnalyzer(resp=repositories)
        output = data_analyzer.create_output_data()
        pprint.pprint(output)

    except requests.exceptions.HTTPError as e:

        print(f"Error occurred for params: {organization}")
        print(f"Exiting the program, detected error {e=}")
        sys.exit(1)

    except ValueError as e:

        print(f"Value Error for params: {organization}")
        print(f"Exiting the program, detected error {e=}")
        sys.exit(1)


if __name__ == "__main__":
    main()
