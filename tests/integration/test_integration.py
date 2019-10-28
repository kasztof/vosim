import pytest
import time
from selenium.webdriver import Chrome


@pytest.fixture
def browser():
    driver = Chrome(executable_path='./chromedriver')
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def test_page_title(browser):
    url = 'localhost:8050'
    browser.get(url)
    time.sleep(1)
    assert browser.title == 'Dash'
