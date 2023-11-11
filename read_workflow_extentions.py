import os
import time

from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

import aroca_logger as al
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

al.aroca_logger()
# Get the environment variables
load_dotenv()
cloud_url = os.getenv("CLOUD_URL")
user_email = os.getenv("CLOUD_USER")
user_password = os.getenv("CLOUD_PASSWORD")
post_migration_url = os.getenv("POST_MIGRATION_URL")
i_frame_post_migration = os.getenv("I_FRAME_POST_MIGRATION")

# Set up the webdriver
driver = webdriver.Chrome(ChromeDriverManager().install())

# Navigate to the webpage
driver.get(cloud_url)

# Start the logger
al.logging.info("Starting the logger")

# Log in
al.logging.info("Logging in")

WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "username")))

driver.find_element_by_id("username").send_keys(user_email)

continue_button = driver.find_element_by_id("login-submit")
continue_button.click()

WebDriverWait(driver, 15).until(EC.visibility_of_element_located((By.ID, "password")))
driver.find_element_by_id("password").send_keys(user_password)

login_button = driver.find_element_by_id("login-submit")
login_button.click()

# wait for the page to load and move on to next url
WebDriverWait(driver, 15).until(EC.url_to_be(cloud_url + "/jira/your-work"))


al.logging.info("Navigating to the workflow page")
# Navigate to the workflow page
driver.get(post_migration_url)


# Switch to iframe for app
al.logging.info("Switching to the iframe")

WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(0))


al.logging.info("Working in iframe")

# driver.switch_to.frame(driver.find_element_by_xpath(i_frame_post_migration))
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located(
        (By.XPATH, '//span[@class="css-178ag6o" and text()="Extension type"]')
    )
)
# Find the button
extension_type = driver.find_element_by_xpath(
    '//span[@class="css-178ag6o" and text()="Extension type"]'
)

# Use JavaScript to click the button
driver.execute_script("arguments[0].click();", extension_type)

# Select workflow
al.logging.info("Selecting workflow")

WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "migratedWorkflow"))
)
workflow_dropdown = driver.find_element_by_id("migratedWorkflow")

workflow_dropdown.click()
