from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import os

#* Scrape data from geekwire funding and save it to index.html
URL = 'https://www.geekwire.com/fundings/'

driver = webdriver.Chrome()
driver.get(URL)

# look for a component with class airtable-embed, then get its src
src = driver.find_element(By.CLASS_NAME, 'airtable-embed').get_attribute('src')
print('Found src:', src)

# visit src
driver.get(src)

time.sleep(5)
def repeat_scroll(driver):
    temp_folder = 'temp'
    if not os.path.exists(temp_folder):
        os.mkdir(temp_folder)
        
    page_height = driver.get_window_size()['height']
    step = 8
        
    scroll_bar = driver.find_element(By.CLASS_NAME, 'antiscroll-scrollbar-vertical')
    for i, pos in enumerate(range(0, page_height, step)):
        print('Iteration:', i)
        print('Current position:%d/%d' % (pos, page_height))
        print('-' * 20)
        with open('%s/index_%d.html' % (temp_folder, i), 'w') as f:
            f.write(driver.page_source)
        
        ActionChains(driver).drag_and_drop_by_offset(scroll_bar, 0, step).click().perform()

        # Wait for a short time to allow content to load
        time.sleep(3)
    
repeat_scroll(driver)
print('Done scraping!')


