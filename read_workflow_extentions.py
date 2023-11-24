import os
import time
from datetime import datetime

from dotenv import load_dotenv
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

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
# driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
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
field_to_add = os.getenv("FIELD_TO_ADD")

# driver = webdriver.Chrome(options=options)


def navigate_to_page():
    # Navigate to the webpage
    driver.get(cloud_url)
    title = driver.title
    options = Options()
    options.add_argument("--auto-open-devtools-for-tabs")
    # Start the logger
    al.logging.info("Starting the logger")

    # Log in
    al.logging.info("Logging in")

    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "username"))
    )

    driver.find_element_by_id("username").send_keys(user_email)

    continue_button = driver.find_element_by_id("login-submit")
    continue_button.click()

    WebDriverWait(driver, 15).until(
        EC.visibility_of_element_located((By.ID, "password"))
    )
    driver.find_element_by_id("password").send_keys(user_password)

    login_button = driver.find_element_by_id("login-submit")
    login_button.click()

    # wait for the page to load and move on to next url
    if cloud_url is not None:
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


def select_workflow():
    # Select workflow

    al.logging.info("Selecting workflow dropdown")

    al.logging.info("Selecting workflow")

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


def expand_fucntions_and_conditions():
    # Open post functions or conditions

    al.logging.info("Opening post functions or conditions")

    expand_post_functions = driver.find_element_by_xpath(
        "//span[@role='img' and @aria-label='Expand row postFunction' and @class='css-1afrefi']"
    )
    expand_conditions = driver.find_element_by_xpath(
        "//span[@role='img' and @aria-label='Expand row condition' and @class='css-1afrefi']"
    )

    rows_to_process = []  # Initialize rows_to_process as an empty list

    if expand_post_functions.is_displayed():
        expand_post_functions.click()
        al.logging.info("Post functions expanded")
        row_group = driver.find_element_by_xpath(
            "//div[@id='tabletreeitem-postFunction']//div[@role='rowgroup']"
        )
        al.logging.info("Counting post functions")
        rows_to_process = row_group.find_elements_by_xpath("//div[@role='row']")

        al.logging.info(f"Found {len(rows_to_process)} post functions")

    return rows_to_process


def process_post_functions_andconditions(rows_to_process):
    for i in range(len(rows_to_process)):
        # Re-find the "Edit" buttons
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, ".//button/span[normalize-space(text())='Edit']")
            )
        )
        edit_buttons = driver.find_elements_by_xpath(
            ".//button/span[normalize-space(text())='Edit']"
        )

        # Click the i-th "Edit" button
        edit_buttons[i].click()
        time.sleep(1)
        time.sleep(1)

        al.logging.info("Switching to default content")

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

        al.logging.info("Config loaded")

        al.logging.info("Getting issue summary")

        time.sleep(1)
        company_name = (
            empty_field
        ) = add_field = summary_field = reporter_field = transition_comment_field = None

        try:
            summary_field = driver.find_element_by_xpath(
                "//span[text()='<%=issue.get(\"summary\")%>']"
            )
            al.logging.info("Summary field found")
        except:
            al.logging.info("Summary field not found")

        try:
            reporter_field = driver.find_element_by_xpath(
                "//span[text()='issue.get(\"assignee\")']"
            )
            al.logging.info("Reporter field found")
        except:
            al.logging.info("Reporter field not found")

        try:
            transition_comment_field = driver.find_element_by_xpath(
                "//span[text()='${transientVars.comment}']"
            )
            al.logging.info("Transition comment field found")
        except:
            al.logging.info("Transition comment field not found")

        try:
            add_field = driver.find_element_by_xpath("//*[@id='s2id_fields']")
            al.logging.info("Add field found")
        except:
            al.logging.info("Add field not found")

        try:
            empty_field = driver.find_element_by_xpath("//label[span[text()=':']]")
            al.logging.info("Empty field-reference found")
        except:
            al.logging.info("Empty field-reference not found")

        try:
            company_name = driver.find_element_by_xpath(
                "//label[span[text()='Company name:']]"
            )
            al.logging.info("Company name field found")
        except:
            al.logging.info("Company name field not found")

        time.sleep(1)

        if summary_field is not None:
            try:
                ActionChains(driver).double_click(summary_field).send_keys_to_element(
                    summary_field, nunjuck_summary
                ).perform()
            except:
                al.logging.info("Error performing action on summary field")

        time.sleep(2)

        if reporter_field is not None:
            try:
                ActionChains(driver).double_click(reporter_field).send_keys_to_element(
                    reporter_field, nunjuck_asignee
                ).perform()
            except:
                al.logging.info("Error performing action on reporter field")

        if transition_comment_field is not None:
            try:
                ActionChains(driver).double_click(
                    transition_comment_field
                ).send_keys_to_element(
                    transition_comment_field, nunjuck_comments
                ).perform()
            except:
                al.logging.info("Error performing action on transition comment field")

        if company_name is None:
            try:
                ActionChains(driver).click(add_field).send_keys_to_element(
                    add_field, field_to_add
                ).send_keys(Keys.ENTER).perform()
                al.logging.info("Add field clicked")

                add_button = driver.find_element_by_xpath(f"//*[text()='Add']")
                al.logging.info("Add button found")

                add_button.click()
                al.logging.info("Add button clicked")

            except:
                al.logging.info("Error performing action on add company name field")

        if empty_field is not None:
            al.logging.info("Empty field found")

            try:
                empty_field.click()
                al.logging.info("Empty field clicked")
            except:
                al.logging.info("Empty field not clicked")

        time.sleep(2)

        try:
            save_button = driver.find_element_by_xpath(
                "//button[normalize-space(text())='Save']"
            )
            al.logging.info("Save button found")
            save_button.click()
            al.logging.info("Save button clicked")
        except:
            al.logging.info("Save button not found")

            al.logging.info("Waiting for post functions to load")

        driver.switch_to.default_content()
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(0))

        raw_html = driver.page_source
        with open(f"output{now}.html", "w", encoding="utf-8") as f:
            f.write(raw_html)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='row']"))
        )

        al.logging.info("Post functions loaded")

        time.sleep(1)


def main():
    navigate_to_page()
    select_workflow()
    rows_to_process = expand_fucntions_and_conditions()
    process_post_functions_andconditions(rows_to_process)


if __name__ == "__main__":
    main()
    pass
