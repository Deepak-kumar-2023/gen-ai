from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Setup Chrome/Brave
options = Options()
options.binary_location = "/usr/bin/google-chrome"  # change this to brave if needed
service = Service("/usr/bin/chromedriver")
driver = webdriver.Chrome(service=service, options=options)

# Open Google only once
driver.get("https://www.google.com")
time.sleep(2)

print("✅ Type your search. Type 'exit' to quit.")

# Run loop until user types 'exit'
while True:
    query = input("🔍 Search Google for: ")

    if query.lower() == "exit":
        print("👋 Exiting... Goodbye Deepak!")
        break
    
    # Open new tab
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])  # switch to new tab
    driver.get("https://www.google.com")
    # time.sleep(2)

    # Clear the old text (if any)
    search_box = driver.find_element(By.NAME, "q")
    search_box.clear()
    search_box.send_keys(query)
    search_box.send_keys(Keys.RETURN)

    time.sleep(3)  # Wait a bit before the next prompt

# Close the browser
driver.quit()
