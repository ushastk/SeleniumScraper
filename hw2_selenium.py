import time
import pandas as pd
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains

driver = webdriver.Chrome()
driver.get('https://www.sothebys.com/en/')
time.sleep(3)

# наведение миши
element_to_hover_over = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div[1]/div/span")
hover = ActionChains(driver).move_to_element(element_to_hover_over)
hover.perform()

# нажатие на кнопку, переход на страницу часы
xpath = '/html/body/div[1]/div/div/div[2]/div[1]/div/div/div[2]/div[2]/div/div[3]/div[5]/div[1]/div'
# Ожидание, пока элемент не станет кликабельным
menu = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, xpath)))
menu.click()

# закрытие вылезающего окна
# before clicking button to open popup, store the current window handle
main_window = driver.current_window_handle
time.sleep(15)
# after opening popup, change window handle
for handle in driver.window_handles:
    if handle != main_window:
        popup = handle
        driver.switch_to_window(popup)
        ads = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.CLASS_NAME, 'bz-close-btn')))
        ads.click()

driver.switch_to.window(driver.window_handles[0])

columns = [
    'Company_name',
    'Description',
    'Price'
]
df = pd.DataFrame(columns=columns)

n = 16
for i in range(1, n + 1):  # перебор страниц
    link = 'https://www.sothebys.com/en/buy/luxury/watches/watch?page=' + str(i) + '&locale=en'
    page = requests.get(link)
    soup = BeautifulSoup(page.text, 'lxml')
    watches = soup.find('ul', class_='gridContent BrowsePage_hitsContainer__sEAG3').find_all('li',
                                                                                             class_='colMediumSpan4 colSmallSpan2 BrowsePage_cardContainer__sdHRW')
    print(i)
    for watch in watches:
        try:
            company_name = watch.find('h5').text
            description = watch.find('p',
                                     class_='paragraph-module_paragraph16Regular__CXt6G undefined grid_card_twoLineClamp__gfLV2').text
            price = watch.find('div', class_='currency_amount_tooltip__qC57W').text
        except AttributeError:
            company_name = ''
            description = ''
            price = ''

        data = {
            'Company_name': company_name,
            'Description': description,
            'Price': price
        }
        print(company_name, price)
        df_watch = pd.DataFrame(data, index=[0])
        df = pd.concat([df, df_watch], ignore_index=True)

df.to_csv('watches.csv')
driver.quit()