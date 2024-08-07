import logging
import os

from news_extractor.yahoo_extractor import YahooExtractor


def define_logger():
    log_file = 'logs/yahoo_extractor.log'
    log_file_path = os.path.abspath(log_file)
    print(f'Log file path: {log_file_path}')

    logging.basicConfig(filename=log_file,
                        level=logging.INFO,
                        format='%(asctime)s | %(name)s | %(levelname)s: %(message)s',
                        datefmt='[%m/%d/%Y %I:%M:%S %p]')


def main():
    LOGGER.info('Initializing news extraction process.')

    phrase_to_search = "Brazil South america rio grande do sul"
    yahoo_extractor = YahooExtractor(LOGGER)
    yahoo_extractor.search_news(message_to_search=phrase_to_search)
    yahoo_extractor.finish_process()

    LOGGER.info('Finishing news extraction process.')


if __name__ == '__main__':
    define_logger()
    LOGGER = logging.getLogger(__name__)

    main()
