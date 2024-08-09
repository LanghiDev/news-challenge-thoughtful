import logging
import os

from news_extractor.yahoo_extractor import YahooExtractor
from news_website.dtos import NewsDTO
import pandas as pd

from datetime import datetime


LOGGER: logging.Logger = logging.getLogger("Yahoo Extractor")
generated_folder = "output"


def management_path():
    if generated_folder not in os.listdir():
        os.mkdir(generated_folder)
    if 'logs' not in os.listdir(generated_folder):
        os.mkdir(f'{generated_folder}/logs')
    if 'excel' not in os.listdir(generated_folder):
        os.mkdir(f'{generated_folder}/excel')
    if 'pictures' not in os.listdir(generated_folder):
        os.mkdir(f'{generated_folder}/pictures')


def define_logger():
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


def main(**kwargs):
    LOGGER.info('Initializing news extraction process.')

    # Unfortunately, Yahoo hasn't category after searching
    while True:
        yahoo_extractor = YahooExtractor(logger=LOGGER, **kwargs)
        news_elements = yahoo_extractor.search_news()
        if not news_elements:
            break
        try_again = yahoo_extractor.get_news_data(news_elements=news_elements)
        if try_again:
            LOGGER.warning("Restarting news extraction process.")
            yahoo_extractor.finish_process()
            continue
        break

    yahoo_extractor.finish_process()

    LOGGER.info("Exporting data to Excel...")
    export_to_excel(yahoo_extractor.news_dtos)

    LOGGER.info('Finishing news extraction process.')


if __name__ == '__main__':
    management_path()
    define_logger()

    parameters = {"phrase_to_search": "NASA", "category": "Science", "months": 2}

    main(**parameters)
