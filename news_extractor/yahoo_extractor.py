import logging
from time import sleep

import SeleniumLibrary.errors
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.remote.webelement import WebElement

from news_website.dtos import NewsDTO
from news_website.xpaths import SEARCH_BAR, SEARCH_BUTTON, NEWS_SECTION, NEWS_BOX, NEWS_IMAGE, NEWS_TITLE, NEWS_DATE, \
    NEWS_DATA
from utils.string_utils import count_phrases_in_title_and_desc, has_money_in_title_and_desc


class YahooExtractor:
    def __init__(self, phrase_to_search: str, logger: logging.Logger):
        self.phrase_to_search = phrase_to_search
        self.logger = logger

        self.news_dtos: list[NewsDTO] = []

        self.url: str = "https://news.yahoo.com"

        self.browser = Selenium()

        self.logger.info(f"Accessing website {self.url}.")
        self.browser.open_browser(self.url, browser="Chrome")

    def search_news(self):
        try:
            self.logger.info(f"Sarching for `{self.phrase_to_search}`...")
            # Typing phrase in search bar
            self.browser.input_text(locator=SEARCH_BAR, text=self.phrase_to_search)
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

            news_elements: list[WebElement] = self.browser.find_elements(locator=NEWS_BOX)
            if not news_elements:
                self.logger.warning(f'News not found with "{self.phrase_to_search}".')
            else:
                self.logger.info("News found!")
            return news_elements

        except Exception:  # noqa
            self.logger.exception("Something got wrong in searching news.")

    def get_news_data(self, news_elements: list[WebElement]):
        news_pictures: list[WebElement] = self.browser.find_elements(locator=NEWS_IMAGE)

        for i, news in enumerate(news_elements):
            try:
                img_src: str = self._get_img_source(news_pictures, news_index=i)
                description: str = self._get_news_description(news)
                # Enter a news
                self.browser.click_element(locator=NEWS_DATA)
                # Extracts title, description, ...
                tabs = self.browser.get_window_handles()
                title: str = self.browser.get_text(locator=NEWS_TITLE)
                if not title:
                    self.logger.info("Trying to extract NEWS data in another tab.")
                    sleep(5)

                    self.browser.driver.switch_to.window(tabs[-1])
                    title = self.browser.get_text(locator=NEWS_TITLE)

                date: str = self.browser.get_text(locator=NEWS_DATE)

                count_phrase: int = count_phrases_in_title_and_desc(self.phrase_to_search, title, description)

                has_money: bool = has_money_in_title_and_desc(title, description)

                self.news_dtos.append(NewsDTO(
                    title=title,
                    date=date,
                    description=description,
                    picture_filename=img_src,  # TODO: download image and consider filename img
                    count_search_phrase=count_phrase,
                    money_news=has_money
                ))

                self.browser.driver.switch_to.window(tabs[-2])
            except Exception:
                self.logger.exception("Something got wrong when extracting news data")

    def finish_process(self):
        self.logger.info("Quiting browser.")
        self.browser.close_browser()

    @staticmethod
    def _get_img_source(news_pictures: list[WebElement], news_index: int):
        return news_pictures[news_index].get_attribute('src')

    @staticmethod
    def _get_news_description(news: WebElement):
        return news.text.split('\n')[-1]
