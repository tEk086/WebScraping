from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

from constructor import SeleniumBrowser
from constructor import search_params, scroll_page
from tqdm import tqdm
import json, time, random


def wait_for(browser, delay: int = 0, by: By = None, element: str = None):
    """
    WebDriverWait for browser=browser with delay=delay
    until expected conditions with presence of element
    located by=by element=element will be satisfied.

    :param browser: browser instance which will wait.
    :param delay: set timeout in seconds.
    :param by: target element locator.
    :param element: target element name.
    :return: selenium object
    """
    try:
        return WebDriverWait(browser, delay).until(EC.presence_of_element_located((by, element)))
    except Exception:
        print(Exception)

def parser(url: str, search_text: str = None, keywords: tuple = None):
    # Getting browser instance and main page content
    USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
    browser = SeleniumBrowser.chrome(headless=False, img_download=False, start_maximized=True, user_agent=USER_AGENT)
    search_page_url = search_params(url, parameters=parameters)
    browser.get(search_page_url)
    main_content = wait_for(browser, 5, By.CLASS_NAME, 'vacancy-serp-content')
    scroll_page(browser, 1000)

    # Collecting vacancies links with pagination
    max_pages = int(main_content.find_element(By.XPATH, '//*[@class="pager"]/span[6]/span[3]/a/span').text)
    vacancies_links = tuple()
    progress_bar = tqdm(range(0, 2), colour = 'green') # range(0, max_pages - 1)
    for page_num in progress_bar:
        next_page_link = search_page_url + f'&page={page_num}'
        browser.get(next_page_link)
        page_content = wait_for(browser, 5, By.ID, 'a11y-main-content')
        scroll_page(browser, 1000)
        vacancies_list = page_content.find_elements(By.XPATH, '//div/div/div/div/h2/span/a')
        for vacancy in vacancies_list:
            vacancies_links = (*vacancies_links, vacancy.get_attribute('href'))
        description = f'| Processing page {page_num + 1} of {max_pages} | Found: {len(vacancies_links)} links | '
        progress_bar.set_description(description)

    # Processing of overall vacancies links with keywords filtration of content
    parsed_data = {}
    progress_bar = tqdm(vacancies_links,colour = 'green')
    for link in progress_bar:
        browser.get(link)
        scroll_page(browser, 100)
        vacancy_description = wait_for(browser, 5, By.CLASS_NAME, 'bloko-columns-row')
        time.sleep(random.uniform(2, 3))
        if all(words in vacancy_description.text.split(' ') for words in keywords):
            salary = vacancy_description.find_element(By.XPATH, '//*[@class="vacancy-title"]/div[2]/span').text
            company_name = vacancy_description.find_element(By.CLASS_NAME, 'vacancy-company-name').text
            address = vacancy_description.find_element(By.CLASS_NAME, 'vacancy-company-redesigned').find_elements(By.TAG_NAME, 'div')[-1].text
            parsed_data[link] = {
                'salary' : salary,
                'company_name' : company_name,
                'address' : address
            }
            with open('head_hunter.json', 'w', encoding='utf-8') as file:
                file.write(json.dumps(parsed_data, ensure_ascii=False))
            print(f'\n{parsed_data[link]}')
        description = f'| {len(parsed_data)} vacancies filtered by keywords: {keywords} | '
        progress_bar.set_description(description)

if __name__ == '__main__':
    SEARCH_TEXT = 'Python'
    KEYWORDS = ('Django', 'Flask')
    CURRENCY = '' # if currency_code not 'EUR' or 'USD' then search will be done for vacancies with salary indicated in rubles
    URL = 'https://hh.ru/search/vacancy?'
    parameters = [
        f'text={SEARCH_TEXT}',
        'salary=',
        'ored_clusters=true',
        'area=1',
        'area=2',
        'hhtmFrom=vacancy_search_list',
        'hhtmFromLabel=vacancy_search_line',
        'items_on_page=100',
        'disableBrowserCache=false',
        'only_with_salary=true',
        f'currency_code={CURRENCY}'
    ]
    parser(URL, search_text=SEARCH_TEXT, keywords=KEYWORDS)
