SEARCH_BAR = '//input[@id="ybar-sbq"]'

SEARCH_BUTTON = '//button[@id="ybar-search"]'

NEWS_SECTION = '//*[@id="horizontal-bar"]//a[contains(text(), "News")]'

NEWS_BOX = '//div[@id="web"]//ol/li'
NEWS_IMAGE = f'{NEWS_BOX}//img'
NEWS_DATA = f'{NEWS_BOX}//a[contains(@class, "thmb")]'

NEWS_TITLE = '//h1'
NEWS_DATE = '//time'
