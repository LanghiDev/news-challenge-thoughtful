from pydantic import BaseModel


class NewsDTO(BaseModel):
    title: str
    date: str
    description: str
    picture_filename: str
    count_search_phrase: int
    money_news: bool
