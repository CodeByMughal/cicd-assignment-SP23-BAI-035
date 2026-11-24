"""Selenium tests for the CI/CD assignment web page.

Edit STUDENT_NAME and ROLL_NUMBER below so they match index.html.
"""
import os
import time
import urllib.request

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

STUDENT_NAME = "Muhammad Mazhar Afzal"
ROLL_NUMBER = "SP23-BAI-035"

BASE_URL = os.getenv("BASE_URL", "http://localhost:8081")
RESULTS_DIR = os.getenv("RESULTS_DIR", "results")


def wait_for_site(url, timeout=30):
    """Staging container may still be starting; poll until it answers."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=3) as r:
                if r.status == 200:
                    return
        except Exception:
            time.sleep(1)
    raise RuntimeError(f"Site not reachable at {url} after {timeout}s")


@pytest.fixture(scope="module")
def driver():
    wait_for_site(BASE_URL)
    opts = Options()
    for arg in ("--headless=new", "--no-sandbox", "--disable-dev-shm-usage",
                "--window-size=1280,900"):
        opts.add_argument(arg)
    chrome_bin = os.getenv("CHROME_BIN")
    if chrome_bin and os.path.exists(chrome_bin):
        opts.binary_location = chrome_bin
    driver_path = os.getenv("CHROMEDRIVER")
    service = Service(driver_path) if driver_path and os.path.exists(driver_path) else Service()
    d = webdriver.Chrome(service=service, options=opts)
    yield d
    d.quit()


@pytest.fixture
def page(driver):
    driver.get(BASE_URL)
    return driver


def test_title(page):
    assert "CI/CD Assignment 3" in page.title
    assert STUDENT_NAME in page.title


def test_heading_shows_name_and_roll(page):
    assert page.find_element(By.ID, "student-name").text == STUDENT_NAME
    assert ROLL_NUMBER in page.find_element(By.ID, "roll-number").text


def test_button_click_shows_message(page):
    page.find_element(By.ID, "greet-btn").click()
    msg = WebDriverWait(page, 5).until(
        EC.text_to_be_present_in_element((By.ID, "message"), "Hello")
    )
    assert msg
    assert page.find_element(By.ID, "message").text == "Hello! The CI/CD pipeline is working."


def test_textbox_input_is_displayed(page):
    text = "Selenium test input 123"
    box = page.find_element(By.ID, "user-input")
    box.clear()
    box.send_keys(text)
    page.find_element(By.ID, "submit-btn").click()
    WebDriverWait(page, 5).until(
        EC.text_to_be_present_in_element((By.ID, "output"), text)
    )
    assert page.find_element(By.ID, "output").text == f"You entered: {text}"

    # Required by the assignment: save one screenshot from a test
    os.makedirs(RESULTS_DIR, exist_ok=True)
    page.save_screenshot(os.path.join(RESULTS_DIR, "textbox_test.png"))
