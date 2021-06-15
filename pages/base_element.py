
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import configparser


class BaseElement(object):
    config = configparser.ConfigParser()
    config.read("config.ini")
    MIN_WAIT_SEC = int(config['DEFAULT']['ELEMENT_MIN_WAIT_SEC'])
    MAX_WAIT_SEC = int(config['DEFAULT']['ELEMENT_MAX_WAIT_SEC'])
    USUAL_WAIT_SEC = int(config['DEFAULT']['ELEMENT_USUAL_WAIT_SEC'])

    def find_elements(self):
        try:
            elements = \
                WebDriverWait(self.driver, self.MAX_WAIT_SEC). \
                until(EC.visibility_of_all_elements_located(
                    locator=self.locator))
            self.web_elements = elements
        except:
            return False

    def __init__(self, driver, locator, single_element=True):
        self.driver = driver
        self.locator = locator
        self.web_element = None
        self.web_elements = None

        if single_element:
            self.find()
        else:
            self.find_elements()

    def find(self):
        try:
            element = \
                WebDriverWait(self.driver, self.MAX_WAIT_SEC). \
                until(EC.visibility_of_element_located(locator=self.locator))
            self.web_element = element
        except:
            return False

    def input_text(self, txt):
        try:
            self.web_element.send_keys(txt)
            return True
        except:
            return False

    def click(self):
        try:
            element = WebDriverWait(self.driver, self.MAX_WAIT_SEC).until(
                EC.element_to_be_clickable(locator=self.locator))
            element.click()
            return True
        except:
            return False

    @property
    def attribute(self, attr_name):
        attribute = self.web_element.get_attribute(attr_name)
        return attribute

    @property
    def text(self):
        text = self.web_element.text
        return text
