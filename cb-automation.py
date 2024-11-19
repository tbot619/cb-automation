from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os

load_dotenv()
# List of names to skip
skip_names = os.getenv("SKIP").split(",")  # Add names you want to skip here

# Set your custom message here
custom_message = os.getenv("MESSAGE")

# Path to the Firefox profile
profile_path = os.getenv("PROFILE")  # Replace with your actual profile
gender = os.getenv("GENDER")
country = os.getenv("COUNTRY")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
b1l = int(os.getenv("BRACKET_1_LOWER"))
b1h = int(os.getenv("BRACKET_1_HIGHER"))
b2l = int(os.getenv("BRACKET_2_LOWER"))
b2h = int(os.getenv("BRACKET_2_HIGHER"))

# Set Firefox options
options = Options()
options.set_preference("profile", profile_path)

# Initialize WebDriver (using Firefox in this example)
driver = webdriver.Firefox(options=options)

# Open the ChatBlink website
driver.get("https://www.chatblink.com/")

# Wait for the page to load and click on the "Login" button
try:
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "login_btn"))
    )
    login_button.click()

    # Wait for the login form to appear
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "login_form"))
    )

    # Fill in the login details (replace with your email and password)
    email_input = driver.find_element(By.ID, "email1")
    password_input = driver.find_element(By.ID, "password1")

    # Replace with your login credentials
    email = os.getenv("EMAIL")  # Replace with your email
    password = os.getenv("PASSWORD") # Replace with your password

    # Clear the fields before entering the data
    email_input.clear()
    password_input.clear()

    # Enter the login credentials
    email_input.send_keys(email)
    password_input.send_keys(password)

    # Submit the form
    login_form = driver.find_element(By.ID, "login_form")
    login_form.submit()

    # Wait for login to complete (you can use an explicit wait here if needed)
    WebDriverWait(driver, 10).until(
        EC.url_changes(driver.current_url)
    )

    print("Login successful!")

except Exception as e:
    print(f"Login failed: {e}")
    driver.quit()


# Set the duration for the script to run (in seconds)
run_duration = 60 * 5  # 30 minutes
start_time = time.time()

# Now we proceed with the original script logic
# Open the ChatBlink users list page after login
driver.get("https://www.chatblink.com/tts#users-main")

messages_sent = 0

try:
    # Wait for users list to load
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, "users-main"))
    )

    # Locate users and filter based on data attributes
    users = driver.find_elements(By.CSS_SELECTOR, "#users-main li")

    for user in users:

        try:
            # Extract the user's name and limit it to the part before the first whitespace
            name_element = user.find_element(By.TAG_NAME, "strong")
            user_name_full = name_element.text
            user_name_first_part = user_name_full.split()[0]  # Get only the part before the first whitespace

            # Check if the first part of the name is in the skip list
            if user_name_first_part in skip_names:
                # print(f"User '{user_name_first_part}' matches a skip name; skipping.")
                continue  # Skip to the next user in the list
            
            # Retrieve attributes
            user_gender = user.get_attribute("data-gender")
            user_country = user.get_attribute("data-country")
            user_age = int(user.get_attribute("data-age"))

            # Check if user matches criteria
            if (
                user_gender == gender and       # Gender
                user_country == country and  # From India
                ((b1l <= user_age <= b1h) 
                 or (b2l <= user_age <= b2h))  # Age range
            ):

                user.click()
                
                # Wait until the loader is hidden, indicating chat is loaded
                WebDriverWait(driver, 10).until(
                    EC.invisibility_of_element_located((By.ID, "loader"))
                )

                # Check if there are existing messages
                msgs = driver.find_elements(By.CSS_SELECTOR, "#msgs li")
                if msgs:
                    time.sleep(1)
                    continue

                text_area = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "msg"))
                )
                text_area.click()

                # Type the custom message into the textarea
                text_area.send_keys(custom_message)

                # Click the "Send" button to send the message
                send_button = driver.find_element(By.ID, "send_message")
                send_button.click()
                messages_sent+=1

                # Navigate back to the users list after sending the message
                time.sleep(1)  # Delay before moving to the next user

        except Exception as e:
            continue

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the driver after completion
    print(f"Users Processed: {len(users)}")
    print(f"Messages sent  : {messages_sent}")