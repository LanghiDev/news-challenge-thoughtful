"""
All Yahoo News xpaths elements that are used on process
"""

SEARCH_BAR = '//input[@id="ybar-sbq"]'

SEARCH_BUTTON = '//button[@id="ybar-search"]'

NEWS_SECTION = '//*[@id="horizontal-bar"]//a[contains(text(), "News")]'

NEWS_BOX = '//div[@id="web"]//ol/li'
NEWS_IMAGE = '//div[contains(@class, "caas-img-container")]//img'
NEWS_DATA = f'{NEWS_BOX}//a[contains(@class, "thmb")]'


NEWS_TITLE = f'{NEWS_BOX}//h4//a'
NEWS_DATE_XPATHS = ['//time', '//div[contains(@class, "timestamp")]']

PAGES = '//div[contains(@class, "pages")]//a'
