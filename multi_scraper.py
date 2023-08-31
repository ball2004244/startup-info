from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from helper import create_folder
from typing import Tuple
import threading
import time
import os

global THREAD_HEALTH
THREAD_HEALTH = {}

# * Return URL of target website
# * Input: URL of initial website
# * Output: URL of target website (destination)


def nav_agent(URL: str) -> Tuple[str, int]:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)

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

    driver.get(src)
    time.sleep(5)

    page_height = driver.get_window_size()['height']
    return src, page_height


# * Define scraping agent
# * Input: URL of target website
# * Output: None

def scrape_agent(URL: str, start: int = 0, end: int = 100, step: int = 8, index: int = 0, temp_folder='temp') -> None:
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_argument("--headless")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    s = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)

    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

    driver.get(URL)
    time.sleep(5)

    repeat_scroll(driver, start=start, end=end, step=step,
                  index=index, temp_folder=temp_folder)
    driver.close()


# * define repeat scroll function
def repeat_scroll(driver, start: int = 0, end: int = 100, step: int = 8, index: int = 0, temp_folder='temp') -> None:
    scroll_bar = driver.find_element(
        By.CLASS_NAME, 'antiscroll-scrollbar-vertical')

    # scroll to start position
    ActionChains(driver).drag_and_drop_by_offset(
        scroll_bar, 0, start).click().perform()

    for i, pos in enumerate(range(start, end, step)):
        with open('%s/index_%d-%d.html' % (temp_folder, index, i), 'w') as f:
            f.write(driver.page_source)

        scroll_bar = driver.find_element(
            By.CLASS_NAME, 'antiscroll-scrollbar-vertical')
        ActionChains(driver).drag_and_drop_by_offset(
            scroll_bar, 0, step).click().perform()

        # Update thread health to cli
        THREAD_HEALTH[index] = [pos - start, end - start]
        
        health_check()
        # wait for page to load
        time.sleep(3)

def health_check() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')
    print('Thread Health')
    print('Scraping with %d agents' % len(THREAD_HEALTH))
    for key, value in THREAD_HEALTH.items():
        print('Agent %d, Progress: %d/%d' % (key, value[0], value[1]))
    print('-' * 20)

def multi_scraping(URL: str, step: int = 8, height: int = 100, num_agents: int = 10, temp_folder='temp') -> None:
    create_folder(temp_folder)
    threads = []
    for i in range(num_agents):
        start = i * height // num_agents
        end = (i + 1) * height // num_agents
        t = threading.Thread(target=scrape_agent, args=(
            URL, start, end, step, i, temp_folder))
        threads.append(t)
        THREAD_HEALTH[i] = [0, end - start]
        t.start()
        # delay between threads
        time.sleep(1)

    for t in threads:
        t.join()


if __name__ == '__main__':
    # * Define initial website
    URL = 'https://www.geekwire.com/fundings/'
    step = 4
    num_agents = 10

    print('Start scraping data from %s' % URL)
    target_URL, page_height = nav_agent(URL)

    print('Start multi-threaded scraping with %d agents' % num_agents)
    multi_scraping(target_URL, step=step,
                   height=page_height, num_agents=num_agents)

    print('Done')
