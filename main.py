from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import time
import requests
import pickle
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.keys import Keys

def login_and_get_cookies(driver, login_url, email, password):
    driver.get(login_url)

    try:
        # Wait for the email input to be present and enter the email
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)

        # Wait for the password input to be present and enter the password
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)

        # Wait for the login button to be clickable and click it
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))).click()

        # Wait for login to complete
        time.sleep(5)
        #input("verify that you logged in then press 'enter'")#uncomment this line if you have to deal with captchas


        driver.get('https://www.lusha.com/')
        # if you want to use cookies to login automatically,
        # you need to be on the same url that you downloaded the cookies from
        # the logged out page is not the same as the dashboard, so you need to use a page
        # that both logged in users and logged out visitors can access,
        # such as https://www.lusha.com/
        time.sleep(5)

        # Get cookies
        cookies = driver.get_cookies()
        with open("cookies.pkl",'wb') as f:
            pickle.dump(cookies,f)
        return cookies

    except Exception as e:
        print(f"Exception occurred during login: {e}")
        print(driver.page_source)  # Print page source for debugging
        raise e

def load_cookies(driver,url):
    driver.get('https://www.lusha.com/')
    # if you want to use cookies to login automatically,
    # you need to be on the same url that you downloaded the cookies from
    # the logged out page is not the same as the dashboard,
    # so you need to use a page that both logged in users and logged out visitors can access,
    # such as https://www.lusha.com/
    time.sleep(2)
    with open('cookies.pkl','rb') as f:
        cookies = pickle.load(f)
        for cookie in cookies:
            try:
                driver.add_cookie(cookie)
            except:
                pass
    driver.get(url)
    time.sleep(2)
    if driver.current_url != url:
        print('current url is:',driver.current_url)
        assert False


def scrape_lusha(company, email, password,driver):
    url = f"https://dashboard.lusha.com/dashboard"

    try:
        
        #note: login may require Captcha solving
        driver.get(url)
        original_window = driver.current_window_handle

        search_box = (By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/span/div/div/span/input")

        WebDriverWait(driver, 20).until(EC.presence_of_element_located(search_box))

        search_box = driver.find_element(*search_box)
        search_box.send_keys(company)
        time.sleep(3)
        #time for dropdown to show

        index = 1
        possible_contacts_xpath = f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div[1]/div/span[{index}]'
        WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, possible_contacts_xpath)))

        text = ''
        while text != 'COMPANIES':
            possible_contacts_xpath = f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div[{index}]/div/span[1]'
            #actual =                   '/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div[5]/div/span[1]'
            try:
                text = driver.find_element(By.XPATH,possible_contacts_xpath).text
            except:
                pass
            index+=1


        print('made with',company)
        while True:
            potential_company_xpath = f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div[{index}]/div/span[1]/div/span'
                                   #= f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div[7]/div/span[1]/div/span'
            try:
                WebDriverWait(driver,3).until(EC.presence_of_element_located((By.XPATH,potential_company_xpath)))
            except:
                index+=1
                continue
            potential_company_selector = driver.find_element(By.XPATH,potential_company_xpath)
            mex_text = ''
            mexico_confirmed_xpath = f'/html/body/div[1]/div[3]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div/div[1]/div[{index}]/div/span[2]/div/div[1]'
            try:
                mexico_confirmed_selector = driver.find_element(By.XPATH,mexico_confirmed_xpath)
                mex_text = mexico_confirmed_selector.text
            except:
                pass
            if company.strip().lower() in potential_company_selector.text.strip().lower()\
                    and 'select' not in potential_company_selector.text.strip().lower()\
                    and ('mx' in mex_text.lower() or 'mex' in mex_text.lower()):
                print(potential_company_selector.text.strip().lower())
                company_text = potential_company_selector.text
                potential_company_selector.click()
                break

            index+=1
        #search_box.send_keys(Keys.RETURN)




        show_details_xpath      = '/html/body/div[1]/div[13]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div/div[1]/div[3]/div/div/button/span'
        show_details_xpath_test = '/html/body/div[1]/div[13]/div[2]/div[2]/div/div[2]/div[3]/div[2]/div/div/div[3]/div/div/button/span'

        show_details_xpath = show_details_xpath_test
        num = 3
        try:
            WebDriverWait(driver,20).until(EC.presence_of_element_located((By.XPATH,show_details_xpath)))
        except:
            show_details_xpath = '/html/body/div[1]/div[13]/div[2]/div[2]/div/div[2]/div[2]/div[2]/div/div/div[3]/div/div/button/span'
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, show_details_xpath)))
            num = 2
        show_details_buttons = driver.find_elements(By.XPATH,show_details_xpath)
        for index in range(len(show_details_buttons)):
            locator = index + 1
            button = show_details_buttons[index]
            if button.text == 'Show details':
                try:

                    builder = ActionChains(driver)

                    builder.scroll_to_element(button)
                    builder.pause(2)
                    builder.move_to_element(button)
                    builder.pause(2)
                    builder.scroll_by_amount(0,200)
                    builder.pause(2)
                    builder.move_to_element(button)
                    builder.pause(2)
                    builder.move_by_offset(0,40)
                    builder.pause(2)
                    builder.click()
                    builder.perform()
                    time.sleep(2)
                    print('unlocked email for',company)
                except Exception as e:
                    print(e)
                    continue
            elif button.text == 'Show emails':
                button.click()
                time.sleep(2)
                print('unlocked email for',company)

            email_xpath = f'/html/body/div[1]/div[13]/div[2]/div[2]/div/div[2]/div[{num}]/div[2]/div/div[{locator}]/div[2]/div[1]/div/div[2]/div[1]/div/div'

            email = driver.find_element(By.XPATH,email_xpath).text
            name_xpath = f'/html/body/div[1]/div[13]/div[2]/div[2]/div/div[2]/div[{num}]/div[2]/div/div[{locator}]/div[1]/div[1]/div[1]'
            name = driver.find_element(By.XPATH,name_xpath).text.split(' ',1)
            first_name = name[0]
            last_names = name[1]
            print(email,first_name,last_names)
            break



        return [company_text,first_name,last_names,email]

    finally:
        pass

# List of companies to scrape
companies = [
    "Artha Capital", "Gobierno del estado", "Lintel", "Colliers International", "Agropark", "Hines",
    "Desarrolladora Marabis", "Gomsa Inmobiliaria", "Grupo Server", "WTC Industrial", "Tres Naciones Parque Industrial",
    # Add more companies as needed
]

# Login URL and credentials
login_url = "https://auth.lusha.com/login?returnUrl=https%3A%2F%2Fdashboard.lusha.com%2Fdashboard"  # Replace with the actual login URL
email = "your.email@here.com"  # Replace with your actual email
password = "Your_password_here*"  # Replace with your actual password


url = f"https://dashboard.lusha.com/dashboard"

# Set up Selenium options
options = Options()
#options.add_argument("--headless")  # Run in headless mode
options.add_argument("--disable-gpu")
options.add_argument("--start-maximized")
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

# Set up the WebDriver
service = ChromeService(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
#driver = webdriver.Chrome()#options=options)


try:
    #assert False
    load_cookies(driver,url)
    print('logged in using cookies')
except FileNotFoundError as e:
    cookies = login_and_get_cookies(driver, login_url, email, password)
    print('logged in and made cookie file')
except AssertionError as e:
    driver = driver.quit()
    #driver = webdriver.Chrome(service=service, options=options)
    driver = webdriver.Chrome(options=options)  
    cookies = login_and_get_cookies(driver, login_url, email, password)
    print('cookies went stale, logged in and made cookie file')

# Scrape contact details from Lusha
data = [['company','first name','last names','email']]
for company in companies:
    print(f"Scraping contacts for {company}:")
    lusha_contacts = False
    try:
        lusha_contacts = scrape_lusha(company, email, password,driver)
    except:
        pass
    if not lusha_contacts:
        print(f"No contacts found or timeout occurred for {company}")
    else:

        print(f'Contact for {company}:{lusha_contacts[2]}, {lusha_contacts[1]}, {lusha_contacts[3]}')
        data.append(lusha_contacts)

with open('./contacts.csv','w') as f:
    for line in data:
        f.write(",".join(line)+'\n')
