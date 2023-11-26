import json
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

# Read the config file
with open("config.json") as f:
    config = json.load(f)

# Convert the current time to a string
current_time = now.strftime("%H:%M:%S")
al.aroca_logger()

# Set up the webdriver
# chrome = os.getenv("CHROME_DRIVER_PATH")
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
# driver = webdriver.Chrome(ChromeDriverManager().install())

# Get the environment variables
load_dotenv()
cloud_url = os.getenv("CLOUD_URL")
user_email = os.getenv("CLOUD_USER")
user_password = os.getenv("CLOUD_PASSWORD")
post_migration_url = os.getenv("POST_MIGRATION_URL")
i_frame_post_migration = os.getenv("I_FRAME_POST_MIGRATION")
workflows = os.getenv("WORKFLOW")
nunjuck_summary = os.getenv("NUNJUCK_SUMMARY")
nunjuck_asignee = os.getenv("NUNJUCK_ASIGNEE")
nunjuck_comments = os.getenv("NUNJUCK_COMMENTS")
nunjuck_access_control = os.getenv("NUNJUCK_ACCESS_CONTROL")
add_company_name = os.getenv("ADD_COMPANY_NAME")
add_software_package = os.getenv("ADD_SOFTWARE_PACKAGE")
add_software_package_version = os.getenv("ADD_SOFTWARE_PACKAGE_VERSION")


# driver = webdriver.Chrome(options=options)


def navigate_to_page():
    # Navigate to the webpage
    driver.get(cloud_url)
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
    al.logging.info("Switching to iframe")

    WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(0))

    al.logging.info("Working in iframe")

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


def select_workflow(workflow):
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

    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, f"//*[text()='{workflow}']"))
    )

    worklfow_name = driver.find_element_by_xpath(f"//*[text()='{workflow}']")

    worklfow_name.click()

    al.logging.info(f"{workflow} selected")


def expand_fucntions_and_conditions():
    # Open post functions or conditions
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located(
            (By.XPATH, "/html/body/section/div[1]/div/div[2]/div[2]/div/div[2]/div")
        )
    )
    try:
        expand_post_functions = driver.find_element_by_xpath(
            "//span[@role='img' and @aria-label='Expand row postFunction' and @class='css-1afrefi']"
        )
    except:
        al.logging.info("Post functions already expanded or not found")

    try:
        expand_conditions = driver.find_element_by_xpath(
            "//span[@role='img' and @aria-label='Expand row condition' and @class='css-1afrefi']"
        )
    except:
        al.logging.info("Conditions already expanded or not found")

    rows_to_process = []  # Initialize rows_to_process as an empty list
    try:
        if expand_post_functions.is_displayed():
            expand_post_functions.click()
            al.logging.info("Post functions expanded")

    except:
        al.logging.info("No post functions found")

    try:
        if expand_conditions.is_displayed():
            expand_conditions.click()
            al.logging.info("Conditions expanded")

    except:
        al.logging.info("No conditions found")

    al.logging.info("Counting post functions")
    rows_to_process = driver.find_elements_by_xpath(
        "//div[@id='tabletreeitem-postFunction']//div[@role='rowgroup']//div[@role='row']"
    )

    al.logging.info(f"Found {len(rows_to_process)} post functions")

    return rows_to_process


def process_post_functions_and_conditions(rows_to_process):
    rows = len(rows_to_process)
    rows = int(rows)
    for i in range(rows):
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

        al.logging.info("Switching to default content")

        driver.switch_to.default_content()

        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//div[@class='aui-dialog2-content']")
            )
        )

        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it(1))
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located(
                (By.XPATH, "//*[@id='content']/div/div[1]/p")
            )
        )
        try:
            post_function_id = driver.find_element_by_xpath(
                "//p[contains(text(), 'Post-function ID:')]"
            )
            al.logging.info(f"Processing {post_function_id.text}")
        except:
            post_function_id = driver.find_element_by_xpath(
                "//*[@id='content']/div/div[1]/p"
            )
            al.logging.info(f"Processing {post_function_id.text}")
        """
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//textarea[@id='summary']"))
            )
        except:
            al.logging.info("Summary field not found")
        """

        al.logging.info("Config loaded")

        al.logging.info("Getting issue summary")

        time.sleep(1)
        label_software_package = (
            software_package
        ) = (
            access_control_update
        ) = (
            company_name
        ) = (
            empty_field
        ) = add_field = summary_field = reporter_field = transition_comment_field = None

        groovy_expressions = config["groovy_expressions"]
        workflows = config["workflows"]
        for expression in groovy_expressions:
            groovy = expression["xpath"]
            nunjuck = expression["nunjuck"]

            try:
                groovy_expression = driver.find_element_by_xpath(groovy)
                al.logging.info(f"Found {groovy}")
                ActionChains(driver).double_click(groovy).send_keys_to_element(
                    groovy, nunjuck
                ).perform()
                al.logging.info(f"Performed action on {groovy}")
            except:
                al.logging.info(f"Could not find {groovy}")

                al.logging.info(f"Error performing action on {groovy}")

            al.logging.info(f"Checking for {groovy} in workflow")
            al.logging.info(f"Replacing with {nunjuck}")

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

        try:
            access_control_update = driver.find_element_by_xpath(
                "//label[span[text()='Access control update:']]"
            )
            al.logging.info("Access Control Update found")
        except:
            al.logging.info("Access Control Update not found")

        try:
            label_software_package = driver.find_element_by_xpath(
                "//label[span[text()='Software package:']]"
            )
            al.logging.info("Software Package found")
        except:
            al.logging.info("Software Package not found")

        try:
            software_package = driver.find_element_by_xpath(
                "//span[@class='css-u1shhv']/i[text()='customfield_17588']"
            )
            al.logging.info("Software Package custom field missing")
        except:
            al.logging.info("Software Package not found")

        try:
            software_package_version = driver.find_element_by_xpath(
                "//span[@class='css-u1shhv']/i[text()='customfield_17643']"
            )
            al.logging.info("Software Package Version custom field missing")
        except:
            al.logging.info("Software Package Version not found")

        try:
            label_software_package_version = driver.find_element_by_xpath(
                "//label[span[text()='Software package version(s):']]"
            )
        except:
            al.logging.info("Software Package Version not found")

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

        if access_control_update is not None:
            try:
                ActionChains(driver).double_click(
                    access_control_update
                ).send_keys_to_element(
                    access_control_update, nunjuck_access_control
                ).perform()
            except:
                al.logging.info("Error performing action on access control update")

        if company_name is None:
            try:
                ActionChains(driver).click(add_field).send_keys_to_element(
                    add_field, add_company_name
                ).send_keys(Keys.ENTER).perform()
                al.logging.info("Add field clicked")

                add_button = driver.find_element_by_xpath(f"//*[text()='Add']")
                al.logging.info("Add button found")

                add_button.click()
                al.logging.info("Add button clicked")

            except:
                al.logging.info("Error performing action on add company name field")

        if software_package is not None and label_software_package is None:
            try:
                ActionChains(driver).click(add_field).send_keys_to_element(
                    add_field, add_software_package
                ).send_keys(Keys.ENTER).perform()
                al.logging.info("Software package clicked")

                add_button = driver.find_element_by_xpath(f"//*[text()='Add']")
                al.logging.info("Software package found")

                add_button.click()
                al.logging.info("Add button clicked")

            except:
                al.logging.info("Error performing action on add software package field")

        if empty_field is not None:
            al.logging.info("Empty field found")

            try:
                empty_field.click()
                al.logging.info("Empty field clicked")
            except:
                al.logging.info("Empty field not clicked")

        time.sleep(2)

        xpaths = [
            "//button/span[normalize-space(text())='Save']",
            "//button[@data-button-name='saveOnly' and normalize-space(text())='Save']",
        ]

        for xpath in xpaths:
            try:
                save_button = driver.find_element_by_xpath(xpath)
                al.logging.info("Save button found")
                save_button.click()
                al.logging.info("Save button clicked")
                break  # If the button is found and clicked, exit the loop
            except Exception as e:
                al.logging.info(
                    f"Failed to find or click the save button with xpath {xpath}: {e}"
                )

        if not save_button:
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
    workflows = config["workflows"]

    navigate_to_page()

    for workflow in workflows:
        workflow_name = workflow["name"]

        select_workflow(workflow_name)
        rows_to_process = expand_fucntions_and_conditions()
        process_post_functions_and_conditions(rows_to_process)


if __name__ == "__main__":
    main()
    pass
