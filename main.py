import logging
import os

from news_extractor.yahoo_extractor import YahooExtractor

LOGGER: logging.Logger = logging.getLogger(__name__)


def define_logger():
    if 'logs' not in os.listdir():
        os.mkdir('logs')
    log_file = 'logs/yahoo_extractor.log'
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


def main():
    LOGGER.info('Initializing news extraction process.')

    phrase_to_search = "Brazil South america rio grande do sul"
    yahoo_extractor = YahooExtractor(phrase_to_search=phrase_to_search, logger=LOGGER)
    news_elements = yahoo_extractor.search_news()
    yahoo_extractor.get_news_data(news_elements=news_elements)
    yahoo_extractor.finish_process()

    LOGGER.info('Finishing news extraction process.')


if __name__ == '__main__':
    define_logger()
    main()
