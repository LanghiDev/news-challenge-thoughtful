import logging
from typing import Optional

import selenium.common.exceptions
from selenium.webdriver.chrome.options import Options
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec

from news_website import xpaths


class BaseSelenium:
    def __init__(self, logger: logging.Logger):
        self.browser: Selenium = Selenium()
        self.logger = logger

        self.load_timeout: int = 10
        self.wait: Optional[WebDriverWait] = None

        self.news_filter_messages: list = ['subscribe to keep reading']
        self.paid_news: str = "needs subscription"

    def open_url(self, url: str):
        self.logger.info(f"Accessing website {url}.")
        self.browser.open_browser(url=url, browser="Chrome", options=self.get_chrome_options())
        self.wait = WebDriverWait(driver=self.browser.driver, timeout=self.load_timeout)

    @staticmethod
    def get_chrome_options() -> Options:
        options: Options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        # options.add_argument('--disable-web-security')
        options.add_argument("--start-maximized")
        return options

    def wait_for_element(self, element_to_wait: tuple[str, str], specific_timeout: float = 0.0):
        wait_backup = self.wait
        if specific_timeout:
            self.wait = WebDriverWait(driver=self.browser.driver, timeout=specific_timeout)

        result = self._try_to_wait_element(ec.visibility_of_element_located(element_to_wait))
        self.wait = wait_backup

        return result

    def wait_for_element_clickable(self, element_to_wait: tuple[str, str]):
        return self._try_to_wait_element(ec.element_to_be_clickable(element_to_wait))

    def _try_to_wait_element(self, message):
        for attempt in range(1, 4):
            try:
                self.wait.until(message)
                return True
            except selenium.common.exceptions.TimeoutException:
                self.logger.debug(f"Element not found. Attempt: {attempt}.")
                if self._filter_paid_news():
                    return self.paid_news
                if attempt == 3:
                    self.logger.error("Impossible to locate element")
                    return False

    def _filter_paid_news(self):
        if any(self.browser.find_element(xpaths.ALL_CONTENT).text.find(msg) >= 0 for msg in self.news_filter_messages):
            self.logger.warning("This news needs subscription from user to keep reading.")
            return True

    def extract_image(self, element_locator: WebElement, img_filename: str):
        self.browser.capture_element_screenshot(locator=element_locator, filename=img_filename)
        return img_filename

    def finish_process(self):
        self.logger.info("Quiting browser.")
        if self.browser:
            self.browser.close_browser()
