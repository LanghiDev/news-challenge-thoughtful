import logging
from typing import Optional

from selenium.webdriver.chrome.options import Options
from RPA.Browser.Selenium import Selenium
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec


class BaseSelenium:
    def __init__(self, logger: logging.Logger):
        self.browser: Selenium = Selenium()
        self.logger = logger

        self.load_timeout: int = 10
        self.wait: Optional[WebDriverWait] = None

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
        if not specific_timeout:
            wait = self.wait
        else:
            wait = WebDriverWait(driver=self.browser.driver, timeout=specific_timeout)

        wait.until(ec.visibility_of_element_located(element_to_wait))

    def wait_for_element_clickable(self, element_to_wait: tuple[str, str]):
        self.wait.until(ec.element_to_be_clickable(element_to_wait))

    def extract_image(self, element_locator: WebElement, img_filename: str):
        self.browser.capture_element_screenshot(locator=element_locator, filename=img_filename)
        return img_filename

    def finish_process(self):
        self.logger.info("Quiting browser.")
        if self.browser:
            self.browser.close_browser()
