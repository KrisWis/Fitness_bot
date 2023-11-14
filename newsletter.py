from time import sleep
from selenium import webdriver

browser = webdriver.Chrome()
browser.implicitly_wait(5) # устанавливаем пятисекундную задержку
# Если Selenium не может найти элемент, он ждет, чтобы все загрузилось и пытается снова

browser.get('https://www.instagram.com/')

# Следующие строки говорят боту найти ссылку с текстом Log in и кликнуть по ней. 
login_link = browser.find_element_by_xpath("//a[text()='Log in']")  
login_link.click()

sleep(50)

browser.close()