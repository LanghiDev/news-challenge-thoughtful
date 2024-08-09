import re
from datetime import datetime, timedelta
import pandas as pd


def get_formatted_date(news_date_text: str):
    date_formats = [
        "%a, %b %d, %Y at %I:%M %p",
        "%a, %b %d, %Y, %I:%M %p",
        "%a, %B %d, %Y at %I:%M %p",
        "%B %d, %Y at %I:%M %p",
        "%b %d, %Y at %I:%M %p",
        "Published %b %d, %Y at %I:%M %p EDT",
        "Published %b %d, %Y at %I:%M %p",
        "%b %d, %Y at %I:%M %p EDT",
        "%b %d, %Y, %I:%M %p BRT",
        "%B %d, %Y",
        "%B, %d %Y"
    ]

    if news_date_text.find('GMT') >= 0:
        news_date_text = news_date_text.split(' GMT')[0]

    for date_format in date_formats:
        try:
            news_date = datetime.strptime(news_date_text, date_format)
            return news_date
        except ValueError:
            continue

    if 'minute' in news_date_text:
        return datetime.now() - timedelta(hours=1)

    if 'hour' in news_date_text:
        hours_ago = int(re.search(r'\d+', news_date_text).group())
        return datetime.now() - timedelta(hours=hours_ago)


def verify_news_date(news_date: datetime, month_range: int) -> bool:
    today: pd.Timestamp = pd.Timestamp(datetime.today().strftime('%Y-%m-%d'))

    if month_range in (0, 1):
        # Verify if news date is in current month
        return today.month == news_date.month

    max_range_selected: pd.Timestamp = today - pd.DateOffset(months=month_range)
    min_date = datetime.strptime(max_range_selected.strftime('%Y-%m-%d'), '%Y-%m-%d')

    return news_date > min_date
