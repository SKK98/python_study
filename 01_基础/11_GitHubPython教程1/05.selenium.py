
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

chrome_driver_path = "D:/SoftWare_Dev/chromedriver.exe" # 将路径替换为你自己的 chromedriver.exe 路径
service = Service(executable_path=chrome_driver_path)
driver = webdriver.Chrome(service=service)
driver.get("https://www.baidu.com")

input_box = driver.find_element(By.ID, 'kw')
input_box.send_keys("苍老师照片")

button = driver.find_element(By.ID, 'su')
button.click()
