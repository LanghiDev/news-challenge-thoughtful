import logging
from datetime import datetime
from time import sleep
from typing import Optional

import SeleniumLibrary.errors
import selenium.common.exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from news_extractor.base_selenium import BaseSelenium
from news_website.dtos import NewsDTO
from news_website import xpaths
from utils.string_utils import count_phrases_in_title_and_desc, has_money_in_title_and_desc
from utils.date_parse import get_formatted_date, verify_news_date


class YahooExtractor(BaseSelenium):
    def __init__(self, logger: logging.Logger, **kwargs):
        super().__init__(logger)
        self.phrase_to_search: str = kwargs["phrase_to_search"]
        self.client_months: int = kwargs["months"]
        self.category: str = kwargs["category"]
        self.news_dtos: list[NewsDTO] = []

        self.url: str = "https://news.yahoo.com"
        self.open_url(self.url)

        self.news_page: int = 1
        self.search_tab: str = ''

        self.pictures_folder = 'pictures'

    def search_news(self):
        try:
            self.logger.info(f"Searching for `{self.phrase_to_search}`...")
            self._do_search()

            # Verify if browser opens a new tab
            sleep(1)
            tabs: list[str] = self._get_all_tabs()
            if not tabs:
                self.logger.error("It's something wrong with DevTools. Interrupting this process.")
                return None
            if len(tabs) > 1:
                self._change_tab(tab=tabs[-1])

            # Click in news section to get only news content
            self.wait_for_element_clickable((By.XPATH, xpaths.NEWS_SECTION))
            self.browser.click_element(locator=xpaths.NEWS_SECTION)

            self.wait_for_element((By.XPATH, xpaths.NEWS_BOX))
            news_elements: list[WebElement] = self.browser.find_elements(locator=xpaths.NEWS_BOX)
            if not news_elements:
                self.logger.warning(f'News not found with "{self.phrase_to_search}".')
            else:
                self.logger.info("News found!")
            return news_elements

        except Exception:  # noqa
            self.logger.exception("Something got wrong in searching news.")

    def get_news_data(self, news_elements: list[WebElement]):
        # Get news elements
        self.wait_for_element((By.XPATH, xpaths.NEWS_DATA))
        news_elements_locators = self.browser.find_elements(xpaths.NEWS_DATA)
        # Get titles elements
        self.wait_for_element((By.XPATH, xpaths.NEWS_TITLE))
        news_titles: list[WebElement] = self.browser.find_elements(xpaths.NEWS_TITLE)
        # Iterates about NEWS, extracting your datas
        for i, news in enumerate(news_elements):
            try:
                title: str = news_titles[i].text
                description: str = self._get_news_description(news)
                # Accesses a news
                status = self._select_news(news_elements_locators, i)
                if status == 'finished':
                    continue

                # Extracts title, description, ...
                if self._doesnt_find_news_data(i):
                    self.logger.error(f"Impossible to extract {i}° news datas.")
                    continue

                img_file: str = self._get_img_filename(picture_index=i)
                date: str = self._verify_news_date(i)
                if date == 'skip':
                    continue
                count_phrase: int = count_phrases_in_title_and_desc(self.phrase_to_search, title, description)
                has_money: bool = has_money_in_title_and_desc(title, description)

                self.logger.info(f"Extracting {i+1}° news from {date}")

                self.news_dtos.append(NewsDTO(
                    title=title,
                    date=date,
                    description=description,
                    picture_filename=img_file,
                    count_search_phrase=count_phrase,
                    money_news=has_money
                ))

                self.browser.close_window()
                self._change_tab(self.search_tab)  # noqa
            except selenium.common.exceptions.WebDriverException:
                self.logger.exception("Erro no DevTools, tentando novamente.")
                return True
            except Exception:  # noqa
                self.logger.exception("Something got wrong when extracting news data")

        self.logger.info("The news on this page is over.")
        self.wait_for_element((By.XPATH, xpaths.PAGES))
        pages: list[WebElement] = self.browser.find_elements(locator=xpaths.PAGES)
        if len(pages) > self.news_page:
            self._go_to_next_page(pages)

    def _doesnt_find_news_data(self, news_index: int, browser_opens_tab: bool = True):
        tabs: list[str] = self._get_all_tabs()
        try:
            self.search_tab = tabs[1]
            news_tab = tabs[2]
        except IndexError:
            news_tab = None
            browser_opens_tab = False

        img_file: str = self._get_img_filename(picture_index=news_index)
        if not img_file and not browser_opens_tab:
            return True

        self._change_tab(news_tab)  # noqa
        return False

    def _select_news(self, news_locator: list[WebElement], index: int):
        try:
            self.browser.click_element(locator=news_locator[index])
        except IndexError:
            return "finished"

    def _go_to_next_page(self, pages: list[WebElement]):
        self.logger.info(f"Going to next page --> {self.news_page+1}")
        self.browser.click_element(pages[self.news_page])
        self.news_page += 1

        self.wait_for_element((By.XPATH, xpaths.NEWS_BOX))
        news_elements: list[WebElement] = self.browser.find_elements(locator=xpaths.NEWS_BOX)

        self.get_news_data(news_elements)

    def _verify_news_date(self, news_index: int) -> str:
        date: str = self._extract_news_date()
        date_adjusted: Optional[datetime] = None
        if not date:
            self.logger.warning("It wasn't possible to extract date from this news website.")
        else:
            date_adjusted: datetime = get_formatted_date(date)
            if not date_adjusted:
                self.logger.warning("Date format not recognized.")
                return "skip"
            else:
                date = date_adjusted.strftime('%Y-%m-%d %I:%M %p')

        if date:
            if not verify_news_date(news_date=date_adjusted, month_range=self.client_months):
                self.logger.info(f"{news_index + 1}° news out of range selected, from {date}. Skipping...")
                return "skip"

        return date

    def _extract_news_date(self):
        date = ''
        for date_xpath in xpaths.NEWS_DATE_XPATHS:
            try:
                self.wait_for_element((By.XPATH, date_xpath), specific_timeout=0.9)
                date = self.browser.get_text(locator=date_xpath)
                break
            except selenium.common.TimeoutException:
                continue
        return date

    def _get_img_filename(self, picture_index: int) -> str:
        img_file: str = ''
        try:
            self.wait_for_element((By.XPATH, xpaths.NEWS_IMAGE), specific_timeout=0.9)
            picture_locator = self.browser.find_element(xpaths.NEWS_IMAGE)
            if picture_locator:
                img_file: str = self.extract_image(
                    element_locator=picture_locator,
                    img_filename=f'{self.pictures_folder}/news_picture_{picture_index + 1}.png')
            else:
                self.logger.error("Not possible to get this news picture.")
        except (SeleniumLibrary.errors.ElementNotFound, selenium.common.exceptions.TimeoutException):
            pass
        return img_file

    def _do_search(self):
        # Typing phrase in search bar
        self.wait_for_element((By.XPATH, xpaths.SEARCH_BAR))
        self.browser.input_text(locator=xpaths.SEARCH_BAR, text=self.phrase_to_search)
        # Click in search button
        self.browser.wait_and_click_button(locator=xpaths.SEARCH_BUTTON)

    def _change_tab(self, tab: str):
        sleep(0.5)
        self.browser.driver.switch_to.window(tab)
        sleep(0.5)

    def _get_all_tabs(self) -> list[str] | None:
        attempts = 1
        for attempts in range(1, 4):
            try:
                tabs: list[str] = self.browser.get_window_handles()
                break
            except selenium.common.exceptions.WebDriverException as err:
                self.logger.warning(f"Error with DevTools. {err.msg}")

        if attempts == 3:
            return None
        return tabs  # noqa

    @staticmethod
    def _get_img_source(news_pictures: list[WebElement], news_index: int):
        return news_pictures[news_index].get_attribute('src')

    @staticmethod
    def _get_news_description(news: WebElement):
        return news.text.split('\n')[-1]
