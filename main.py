import logging
import os

from news_extractor.yahoo_extractor import YahooExtractor
from news_website.dtos import NewsDTO
import pandas as pd

from datetime import datetime


LOGGER: logging.Logger = logging.getLogger(__name__)
generated_folder = "generated"

def define_logger():
    if 'logs' not in os.listdir(generated_folder):
        os.mkdir(f'{generated_folder}/logs')

    log_file = f'{generated_folder}/logs/yahoo_extractor.log'
    log_file_path = os.path.abspath(log_file)
    print(f'Log file path: {log_file_path}')

    LOGGER.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    console_handler = logging.StreamHandler()

    formatter = logging.Formatter(fmt='%(asctime)s | %(name)s | %(levelname)s: %(message)s',
                                  datefmt='[%m/%d/%Y %I:%M:%S %p]')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    file_handler.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)

    # Add handlers to the logger
    LOGGER.addHandler(file_handler)
    LOGGER.addHandler(console_handler)


def export_to_excel(news_list: list[NewsDTO]):
    df = pd.DataFrame(news.model_dump() for news in news_list)
    excel_name: str = f'news_data_{datetime.now().month}-{datetime.now().day}.xlsx'
    df.to_excel(f'{generated_folder}/excel/{excel_name}', index=False, engine='openpyxl')
    LOGGER.info(f"Exported into {excel_name} Excel file.")


def main(phrase_to_search: str, category: str, months: int):
    LOGGER.info('Initializing news extraction process.')

    # Unfortunately, Yahoo hasn't category after searching

    yahoo_extractor = YahooExtractor(phrase_to_search=phrase_to_search, months=months, logger=LOGGER)
    news_elements = yahoo_extractor.search_news()
    if news_elements:
        yahoo_extractor.get_news_data(news_elements=news_elements)
    yahoo_extractor.finish_process()

    LOGGER.info("Exporting data to Excel...")
    export_to_excel(yahoo_extractor.news_dtos)

    LOGGER.info('Finishing news extraction process.')


if __name__ == '__main__':
    define_logger()

    search_phrase = "Brazil south"
    category = "Science"
    months = 0
    main(phrase_to_search=search_phrase, category=category, months=months)
