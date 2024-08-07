import logging
from time import sleep

import SeleniumLibrary.errors
from RPA.Browser.Selenium import Selenium
from news_website.xpaths import SEARCH_BAR, SEARCH_BUTTON, NEWS_SECTION, NEWS_BOX


class YahooExtractor:
    def __init__(self, logger: logging.Logger):
        self.logger = logger

        self.url: str = "https://news.yahoo.com"

        self.browser = Selenium()

        self.logger.info(f"Accessing website {self.url}.")
        self.browser.open_browser(self.url, browser="Chrome")

    def search_news(self, message_to_search: str):
        try:
            self.logger.info(f"Sarching for `{message_to_search}`...")
            # Typing phrase in search bar
            self.browser.input_text(locator=SEARCH_BAR, text=message_to_search)
            # Click in search button
            self.browser.click_button(locator=SEARCH_BUTTON)
            # Click in news section to get only news content
            try:
                self.browser.click_element(locator=NEWS_SECTION)
            except SeleniumLibrary.errors.ElementNotFound:
                self.logger.info("Trying to get NEWS in another tab.")
                sleep(5)
                tabs = self.browser.get_window_handles()
                self.browser.driver.switch_to.window(tabs[-1])
                self.browser.click_element(locator=NEWS_SECTION)
            news_text: str = self.browser.get_text(locator=NEWS_BOX)
        except Exception:  # noqa
            self.logger.exception("Something got wrong in searching news.")

    def finish_process(self):
        self.logger.info("Quiting browser.")
        self.browser.close_browser()
