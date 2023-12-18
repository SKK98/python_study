
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

# https://mp.weixin.qq.com/s/lXXDfzyLVrf3f-aqJN1C3A

# 打开浏览器 进入网页 搜索关键字 q 并回车
if __name__ == "__main__":
    service = Service('D:\SoftWare_Dev\chromedriver.exe')
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.python.org")
    assert "Python" in driver.title
    elem = driver.find_element("name", "q")
    elem.send_keys("pycon")
    elem.send_keys(Keys.RETURN)
    print(driver.page_source)








