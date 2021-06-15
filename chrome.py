from selenium import webdriver
from selenium.webdriver.remote.command import Command


class Chrome(object):

    def __init__(self, browser_options, driver="chromedriver"):

        if driver == "chromedriver":

            chrome_options = webdriver.ChromeOptions()

            for br_option in browser_options:
                chrome_options.add_argument(br_option)

            # chrome_options.add_argument("--incognito")
            chrome_options.add_experimental_option("excludeSwitches",
                                                   ['enable-automation'])
            # chrome_options.add_argument("--disable-extensions")
            # chrome_options.add_argument("--disable-plugins-discovery")

            browser = webdriver.Chrome(chrome_options=chrome_options)
            browser.delete_all_cookies()
            browser.set_window_size(1280, 800)
            browser.set_window_position(0, 0)

            self.browser_options = chrome_options
            self.browser = browser



    def get_status(self):
        try:
            self.browser.execute(Command.STATUS)
            return True
        except ():
            return False
