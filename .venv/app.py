import time
import random
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains


# Function to create a random User-Agent
def get_random_user_agent():
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 10; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
        # Add more user agents as needed
    ]
    return random.choice(user_agents)

# Set up the Selenium WebDriver with a random User-Agent
options = webdriver.ChromeOptions()
options.add_argument(f"user-agent={get_random_user_agent()}")
options.add_argument('--headless')  # Run in headless mode for efficiency
driver = webdriver.Chrome(options=options)

# Prepare the CSV file
csv_file = 'IMDb_data.csv'
csv_columns = ['Title', 'Year', 'Runtime', 'Rated', 'Genres', 'Rating', 'Summary', 'Director', 'Stars']

try:
    # Open the target webpage
    driver.get('https://www.imdb.com/search/title/?title_type=feature&release_date=2000-01-01,2024-12-31')
    actions = ActionChains(driver)

    # Introduce a random delay between actions
    time.sleep(random.uniform(2, 5))

    # Wait for the button to be clickable and then click it
    button = WebDriverWait(driver, 20).until(
        ec.element_to_be_clickable((By.CLASS_NAME, 'dli-info-icon'))
    )
    button.click()

    # Wait for the loader to disappear before proceeding
    WebDriverWait(driver, 10).until(
        ec.invisibility_of_element_located((By.CSS_SELECTOR, 'div[data-testid="loader"]'))
    )

    # Wait for the popup to appear
    popup = WebDriverWait(driver, 10).until(
        ec.visibility_of_element_located((By.CLASS_NAME, 'ipc-promptable-base__content'))
    )

    # Extract data
    metadata_items = popup.find_elements(By.CSS_SELECTOR, 'ul[data-testid="btp_ml"] li')
    year = metadata_items[0].text if len(metadata_items) > 0 else None
    runtime = metadata_items[1].text if len(metadata_items) > 1 else None
    rated = metadata_items[2].text if len(metadata_items) > 2 else None

    genre_items = popup.find_elements(By.CSS_SELECTOR, 'ul[data-testid="btp_gl"] li')
    genres = [item.text for item in genre_items]

    rating_element = popup.find_element(By.CSS_SELECTOR, '.ipc-rating-star--rating')
    rating = rating_element.text if rating_element else None

    title_element = popup.find_element(By.CSS_SELECTOR, '.ipc-title--title')
    title = title_element.text

    parent_element = title_element.find_element(By.XPATH, '../../..')
    second_child = parent_element.find_element(By.XPATH, './*[@class][2]')
    summary = second_child.text

    director_element = popup.find_element(By.CSS_SELECTOR, 'div[data-testid="p_ct_dr"] .ipc-inline-list__item a')
    director_name = director_element.text

    cast_elements = popup.find_elements(By.CSS_SELECTOR, 'div[data-testid="p_ct_cst"] .ipc-inline-list__item a')
    cast_names = [element.text for element in cast_elements]

    # Prepare data for CSV
    data = {
        'Title': title,
        'Year': year,
        'Runtime': runtime,
        'Rated': rated,
        'Genres': ', '.join(genres),
        'Rating': rating,
        'Summary': summary,
        'Director': director_name,
        'Stars': ', '.join(cast_names)
    }

    # Write data to CSV
    with open(csv_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=csv_columns)
        if file.tell() == 0:  # Write header only if file is empty
            writer.writeheader()
        writer.writerow(data)

    print(f"\"{title}\" successfully written to {csv_file}")

    x_offset = random.randint(90, 110)
    y_offset = random.randint(90, 110)
    actions.move_by_offset(x_offset, y_offset).click().perform()

    # Introduce a random delay before finishing
    time.sleep(random.uniform(2, 5))

except Exception as e:
    print(f"An error occurred: {e}")

finally:
    # Close the WebDriver
    driver.quit()
