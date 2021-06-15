from selenium.webdriver.common.by import By
from pages.locator import Locator
from pages.base_element import BaseElement


class BasePage(object):

    URL = None
    LOGOFF_LINK_CSS_LOCATOR = "[data-qa='mainmenu_logoffUser']"
    USER_ICON_CSS_SELECTOR = ".supernova-icon_profile"
    CAPTCHA_TEXT_LOCATOR = "Я не робот"

    def __init__(self, driver):
        self.driver = driver

    def go(self):
        self.driver.get(self.URL)

    @property
    def authorized_UserIcon(self):
        # Иконка авторизованного пользователя
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.USER_ICON_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def logoff_link(self):
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.LOGOFF_LINK_CSS_LOCATOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def captcha_warning(self):
        locator = Locator(by=By.LINK_TEXT, value=self.CAPTCHA_TEXT_LOCATOR)
        return BaseElement(
            driver=self.driver,
            locator=locator,
            single_element=False
        )

    def log_off(self):
        authorized_icon = self.authorized_UserIcon
        if (authorized_icon.web_element is not None):
            if authorized_icon.click():
                try:
                    self.logoff_link.click()
                except:
                    pass
