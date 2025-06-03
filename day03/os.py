from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time

# Chrome options
options = Options()
# You can add more options like headless mode if needed
# options.add_argument("--headless")  # Optional: run without opening a window

# Path to Chrome binary (usually this is the default)
options.binary_location = "/usr/bin/google-chrome"

# Path to chromedriver
service = Service("/usr/bin/chromedriver")

# Launch the browser
driver = webdriver.Chrome(service=service, options=options)

# Open a website
driver.get("https://github.com")

# Wait for 10 seconds
time.sleep(10)

# Close the browser
driver.quit()
