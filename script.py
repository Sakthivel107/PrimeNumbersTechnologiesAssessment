from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

# Setup Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Disable for debugging
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")

# Initialize WebDriver
driver = webdriver.Chrome(options=chrome_options)

url = "https://rera.odisha.gov.in/projects/project-list"
driver.get(url)

# Wait for the "View Details" buttons
try:
    WebDriverWait(driver, 30).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.btnView"))
    )
except Exception as e:
    driver.save_screenshot("error.png")
    driver.quit()
    raise Exception("Failed to load project list. Screenshot saved as error.png")

# Find the first 6 "View Details" buttons
projects = driver.find_elements(By.CSS_SELECTOR, "a.btnView")[:6]
project_data = []

# Open each project detail in the same window
for index, project in enumerate(projects):
    project_url = project.get_attribute("href")
    driver.get(project_url)

    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, "prosummary"))
        )
    except Exception as e:
        print(f"Failed to load detail for project {index+1}")
        continue

    def get_field(label):
        try:
            elem = driver.find_element(By.XPATH, f"//td[contains(text(), '{label}')]/following-sibling::td")
            return elem.text.strip()
        except:
            return "N/A"

    rera_no = get_field("Rera Registration Number")
    project_name = get_field("Project Name")

    try:
        promoter_tab = driver.find_element(By.XPATH, "//a[contains(text(), 'Promoter Details')]")
        promoter_tab.click()
        time.sleep(2)
    except:
        print("Promoter tab not found.")
        continue

    promoter_name = get_field("Company Name")
    promoter_address = get_field("Registered Office Address")
    gst_no = get_field("GST No.")

    project_data.append({
        "Rera Regd. No": rera_no,
        "Project Name": project_name,
        "Promoter Name": promoter_name,
        "Promoter Address": promoter_address,
        "GST No": gst_no
    })

    print(f"[{index + 1}] Project Scraped: {project_name}")
    driver.back()
    time.sleep(2)

driver.quit()

# Display results
df = pd.DataFrame(project_data)
print("\nExtracted Project Data:\n")
print(df.to_string(index=False))
