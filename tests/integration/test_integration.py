import pytest
import time
from selenium.webdriver import Chrome
from selenium import webdriver


@pytest.fixture
def browser():
    driver = Chrome(executable_path='./chromedriver')
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


def load_network(browser):
    url = 'localhost:8050'
    browser.get(url)
    konect_button = browser.find_element_by_id('open-konect-modal')
    konect_button.click()

    load_tab = browser.find_element_by_link_text('Load network')
        
    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(load_tab, 295, 120)
    action.click()
    action.perform()

    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(load_tab, 295, 180)
    action.click()
    action.perform()

    load_button = browser.find_element_by_id('load-konect-network')
    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(load_button, 10, 10)
    action.click()
    action.perform()

    close_button = browser.find_element_by_id('close-konect-modal')
    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(close_button, 10, 10)
    action.click()
    action.perform()

    time.sleep(1)


def test_page_title(browser):
    url = 'localhost:8050'
    browser.get(url)
    time.sleep(1)
    assert browser.title == 'Vosim'


def test_disabled_simulation_tab(browser):
    url = 'localhost:8050'
    browser.get(url)
    simulation_tab = browser.find_element_by_link_text('Simulation')
    
    assert 'disabled' in simulation_tab.get_attribute('class')


def test_disabled_stats_tab(browser):
    url = 'localhost:8050'
    browser.get(url)
    simulation_tab = browser.find_element_by_link_text('Statistics')
    
    assert 'disabled' in simulation_tab.get_attribute('class')


def test_disabled_download_button(browser):
    url = 'localhost:8050'
    browser.get(url)
    simulation_tab = browser.find_element_by_link_text('Download activations')
    
    assert 'disabled' in simulation_tab.get_attribute('class')


def test_load_konect_network(browser):
    load_network(browser)

    simulation_tab = browser.find_element_by_link_text('Simulation')
    statistics_tab = browser.find_element_by_link_text('Statistics')
    
    assert 'disabled' not in simulation_tab.get_attribute('class')
    assert 'disabled' not in statistics_tab.get_attribute('class')


def test_network_stats(browser):
    load_network(browser)

    stats_tab = browser.find_element_by_id('table-network-info')
    all_children_by_css = stats_tab.find_elements_by_css_selector("tr")
    assert len(all_children_by_css) == 4


def test_network_change_layout(browser):
    load_network(browser)

    browser.find_element_by_link_text('Layout').click()

    layout_dropdown = browser.find_element_by_id('layout-dropdown')

    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(layout_dropdown, 10, 10)
    action.click()
    action.perform()

    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(layout_dropdown, 10, 80)
    action.click()
    action.perform()

    time.sleep(2)


def test_run_simulation(browser):
    load_network(browser)

    browser.find_element_by_link_text('Simulation').click()

    treshold = browser.find_element_by_id('treshold')
    treshold.clear()
    treshold.send_keys("0.4")

    init_nodes_num = browser.find_element_by_id('initial-nodes-number')
    init_nodes_num.clear()
    init_nodes_num.send_keys("2")

    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(init_nodes_num, -50, 0)
    action.click()
    action.perform()

    dropdown_node = browser.find_element_by_id('react-select-3--value')
    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(dropdown_node, 10, 50)
    action.click()
    action.perform()
   
    start_button = browser.find_element_by_id('start-button')
    action = webdriver.common.action_chains.ActionChains(browser)
    action.move_to_element_with_offset(start_button, 10, 10)
    action.click()
    action.perform()

    time.sleep(1)

    slider = browser.find_element_by_class_name('rc-slider-step')
    all_children_by_css = slider.find_elements_by_css_selector("span")
    assert len(all_children_by_css) != 0
