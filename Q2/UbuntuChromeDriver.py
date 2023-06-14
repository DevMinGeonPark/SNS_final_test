from selenium import webdriver

class UbuntuChromeDriver(webdriver.Chrome):
    def __init__(self, driver_path="/usr/bin/chromedriver", headless=True, disable_gpu=True):
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument("headless")
        if disable_gpu:
            options.add_argument("--disable-gpu")
        options.add_argument('window-size=1920x1080')
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
        options.add_argument("lang=ko_KR") # 한국어!
        super().__init__(executable_path=driver_path, options=options)

    def __del__(self):
        self.quit()
