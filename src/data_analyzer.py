import logging
import os
from dataclasses import dataclass, field

import pandas as pd

from data_model import OutputData, ResponseData

logger = logging.getLogger(__name__)

STAR_COLUMN = os.getenv("STAR_COLUMNS", "stargazers_count")


@dataclass
class DataAnalyzer:
    """Class that contains all logics to analyze the repositories."""

    resp: list[ResponseData]

    data: pd.DataFrame = field(default=None, init=False)

    def create_output_data(self) -> OutputData:
        """Create output data of required format.

        Returns:
            OutputData: Data Model for required format.
        """
        self._make_dataframe()

        logger.debug("Inside output shape", self.data.shape)
        output = OutputData(
            total_repositories=self.total_repositories,
            total_stars=self.total_stars,
            most_popular_language=self.most_common_language,
            top_5_repositories=self.get_top_5_repository(),
        )
        return output.model_dump()

    def _make_dataframe(self):
        """Creates dataframe from list of ResponseData.

        Raises:
            ValueError: If there are no dataframe created.
            ValueError: If the organization has zero repository.
        """
        self.data = pd.DataFrame([repo.model_dump() for repo in self.resp])

        if self.data is None:
            raise ValueError("no response received.")

        if self.data.shape[0] == 0:
            raise ValueError("There is no repository for this account")

    @property
    def total_stars(self):
        """Number of stars count from all repositories."""
        return self.data[STAR_COLUMN].sum()

    @property
    def total_repositories(self):
        """Number of repositories the organization has."""
        return self.data.shape[0]

    @property
    def most_common_language(self):
        """The statistical mode of languages uses within this organization."""
        return self.data["language"].mode().values[0]

    def get_top_5_repository(self):
        """Top 5 repository within the organization based on star counts."""
        top_5_index = self.data[STAR_COLUMN].sort_values(ascending=False).head(5).index
        required_data = self.data[["name", STAR_COLUMN]]
        required_data = required_data.rename(columns={STAR_COLUMN: "stars"})

        top_5_repo = [required_data.loc[i].to_dict() for i in top_5_index]

        return top_5_repo
