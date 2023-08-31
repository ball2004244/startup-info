from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from helper import create_folder
import time
import threading

# * Scrape data from geekwire funding and save it to index.html


def scrape_data(URL: str, step: int = 8) -> None:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)
    # driver = webdriver.Chrome()

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )
    driver.get(URL)

    src = driver.find_element(
        By.CLASS_NAME, 'airtable-embed').get_attribute('src')
    print('Found src:', src)

    # visit src
    driver.get(src)

    time.sleep(5)

    # scroll till the end of the page
    repeat_scroll(driver, step=step)

    driver.close()


def repeat_scroll(driver, step=8, temp_folder='temp') -> None:
    create_folder(temp_folder)

    page_height = driver.get_window_size()['height']

    scroll_bar = driver.find_element(
        By.CLASS_NAME, 'antiscroll-scrollbar-vertical')
    for i, pos in enumerate(range(0, page_height, step)):
        print('Iteration:', i)
        print('Current position:%d/%d' % (pos, page_height))
        print('-' * 20)
        with open('%s/index_%d.html' % (temp_folder, i), 'w') as f:
            f.write(driver.page_source)

        ActionChains(driver).drag_and_drop_by_offset(
            scroll_bar, 0, step).click().perform()

        # Wait for a short time to allow content to load
        time.sleep(3)


def multi_thread_scroll(driver, num_thread: int = 4, step: int = 8, temp_folder='temp') -> None:
    create_folder(temp_folder)
    pass


def scroll_agent(driver, start: int, end: int, step: int = 8, temp_folder='temp') -> None:
    pass


if __name__ == '__main__':
    URL = 'https://www.geekwire.com/fundings/'

    print('Start scraping data from %s' % URL)
    print('Scraping in progress...')
    scrape_data(URL, step=8)
    print('Done scraping!')
