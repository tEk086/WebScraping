from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from selenium_stealth import stealth
from fake_useragent import UserAgent


class SeleniumBrowser:
    """
    Class implements different selenium browser instances are ready to be used
    """
    @staticmethod
    def chrome(**kwargs) -> object:
        """
        :return: Chrome browser instance
        """
        options = Options()
        options.page_load_strategy = 'eager'

        if 'start_maximized' in kwargs and kwargs['start_maximized']:
            options.add_argument("start-maximized")

        if 'user_agent' not in kwargs:
            options.add_argument(f"user-agent={UserAgent().random}")
        options.add_argument(f"user-agent={kwargs['user_agent']}")

        if 'headless' in kwargs and kwargs['headless']:
            options.add_argument("--headless")

        if 'img_download' in kwargs and not kwargs['img_download']:
            options.add_argument("--blink-settings=imagesEnabled=false")
            options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

        service = Service(executable_path=ChromeDriverManager().install())
        driver = Chrome(service=service, options=options)
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True,
                )
        return driver


def search_params(url: str, parameters: list) -> str:
    """
    :param url:
    :param parameters:
    :return:
    """
    url += '&'.join(param for param in parameters)
    return url


def scroll_page(browser, scroll_step: int = 100) -> None:
    """
    :param browser: The browser to scroll current page
    :param scroll_step: scrolling step in pixels
    """
    total_height = int(browser.execute_script("return document.body.scrollHeight"))
    for i in range(0, total_height, scroll_step):
        browser.execute_script(f"window.scrollTo(0, {i});")
    browser.execute_script(f"window.scrollTo(0, 0);")
