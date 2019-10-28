from selenium import webdriver
from selenium.webdriver.common.keys import Keys

driver = webdriver.Chrome('./chromedriver')

driver.get('localhost:8050')

print(driver.title)

driver.close()