from pydantic import BaseModel


class ResponseData(BaseModel):
    """Pydantic model defined to store initial repo api response."""

    name: str
    description: str | None
    stargazers_count: int
    forks_count: int
    language: str | None


class OutputData(BaseModel):
    """Pydantic model defined for output data."""

    total_repositories: int
    total_stars: int | None
    most_popular_language: str | None
    top_5_repositories: list[dict]
