import os
import time
from datetime import datetime

from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager

import aroca_logger as al
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

# Get the current time
now = datetime.now()

# Convert the current time to a string
current_time = now.strftime("%H:%M:%S")
al.aroca_logger()


# Set up the webdriver
chrome = os.getenv("CHROME_DRIVER_PATH")
driver = webdriver.Chrome(ChromeDriverManager().install())


# driver = webdriver.Chrome(chrome)
# Get the environment variables
load_dotenv()
cloud_url = os.getenv("CLOUD_URL")
user_email = os.getenv("CLOUD_USER")
user_password = os.getenv("CLOUD_PASSWORD")
post_migration_url = os.getenv("POST_MIGRATION_URL")
i_frame_post_migration = os.getenv("I_FRAME_POST_MIGRATION")
workflow = os.getenv("WORKFLOW")
nunjuck_summary = os.getenv("NUNJUCK_SUMMARY")
nunjuck_asignee = os.getenv("NUNJUCK_ASIGNEE")
nunjuck_comments = os.getenv("NUNJUCK_COMMENTS")

# driver = webdriver.Chrome(options=options)

# Navigate to the webpage
driver.get(cloud_url)
title = driver.title
options = Options()
options.add_argument("--auto-open-devtools-for-tabs")
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
al.logging.info("Selecting workflow dropdown")

WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.ID, "migratedWorkflow"))
)
workflow_dropdown = driver.find_element_by_id("migratedWorkflow")

workflow_dropdown.click()

# Select the workflow
al.logging.info("Searching for workflow")
WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.CLASS_NAME, "css-4mp3pp-menu"))
)

workflow_dropdown_search = driver.find_element_by_class_name("css-4mp3pp-menu")
workflow_dropdown_search_html = workflow_dropdown_search.get_attribute("outerHTML")

WebDriverWait(driver, 10).until(
    EC.visibility_of_element_located((By.XPATH, f"//*[text()='{workflow}']"))
)

worklfow_name = driver.find_element_by_xpath(f"//*[text()='{workflow}']")

worklfow_name.click()

al.logging.info("Workflow selected")

# Open post functions or conditions

al.logging.info("Opening post functions or conditions")

expand_post_functions = driver.find_element_by_xpath(
    "//span[@role='img' and @aria-label='Expand row postFunction' and @class='css-1afrefi']"
)
expand_conditions = driver.find_element_by_xpath(
    "//span[@role='img' and @aria-label='Expand row condition' and @class='css-1afrefi']"
)


if expand_post_functions.is_displayed():
    expand_post_functions.click()
    al.logging.info("Post functions expanded")
    row_group = driver.find_element_by_xpath(
        "//div[@id='tabletreeitem-postFunction']//div[@role='rowgroup']"
    )
    al.logging.info("Counting post functions")
    rows_to_process = row_group.find_elements_by_xpath("//div[@role='row']")

    al.logging.info(f"Found {len(rows_to_process)} post functions")
    row_index = 0

    for row in rows_to_process:
        al.logging.info(f"Processing row{row}")

        row.click()
        al.logging.info("Row clicked")
        time.sleep(1)
        al.logging.info("Waiting for edit button")
        edit_button = driver.find_element_by_xpath(f"//*[text()='Edit']")
        al.logging.info("Edit button found")
        edit_button.click()
        al.logging.info("Switching iframe")
        # WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(0))
        al.logging.info("Creating html file")

        body = driver.find_element_by_xpath("//body[@class='aui-page-hybrid']")

        driver.switch_to.default_content()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='aui-dialog2-content']")
            )
        )
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(1))

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//textarea[@id='summary']"))
        )

        row_index += 1
        al.logging.info("Config loaded")

        al.logging.info("Getting issue summary")

        time.sleep(1)
        summary_field = driver.find_element_by_xpath(
            "//span[text()='<%=issue.get(\"summary\")%>']"
        )
        reporter_field = driver.find_element_by_xpath(
            "//span[text()='issue.get(\"assignee\")']"
        )
        transition_comment_field = driver.find_element_by_xpath(
            "//span[text()='${transientVars.comment}']"
        )
        time.sleep(1)

        try:
            ActionChains(driver).double_click(summary_field).send_keys_to_element(
                summary_field, nunjuck_summary
            ).perform()
        except:
            al.logging.info("Summary field not found")

        time.sleep(2)

        try:
            ActionChains(driver).double_click(reporter_field).send_keys_to_element(
                reporter_field, nunjuck_asignee
            ).perform()
        except:
            al.logging.info("Reporter field not found")

        try:
            ActionChains(driver).double_click(
                transition_comment_field
            ).send_keys_to_element(transition_comment_field, nunjuck_comments).perform()
        except:
            al.logging.info("Transition comment field not found")

        time.sleep(2)

        save_button = driver.find_element_by_xpath(
            "//button[normalize-space(text())='Save']"
        )
        save_button.click()

        time.sleep(1)
