from selenium.webdriver.common.by import By

from pages.base_element import BaseElement
from pages.base_page import BasePage
from pages.locator import Locator

import logger
import logging


class HhMainPage(BasePage):

    URL = 'https://hh.ru/'

    BUTTON_REGION_CSS_SELECTOR = "body.l-ambient.s-friendly.custom-font-allowed:nth-child(2) div.Bloko-Notification-Manager.notification-manager:nth-child(1) div.bloko-notification div.bloko-notification__wrapper div.bloko-notification__plate div.bloko-notification__body div.bloko-notification__content.Bloko-Notification-Content div.HH-Supernova-RegionClarification-Content div.supernova-region-clarification-wrapper > button.bloko-button.bloko-button_small.bloko-button_primary.HH-Supernova-RegionClarification-Confirm"
    USER_ICON_CSS_SELECTOR = ".supernova-icon_profile"
    BUTTON_SIGNIN_TEXT = "Войти"
    USERNAME_CSS_SELECTOR = ".HH-AuthForm-Login"
    USERPASS_CSS_SELECTOR = "[type='password']"
    SIGNIN_BUTTON_CSS_SELECTOR = "[class='supernova-navi                             supernova-navi_lvl-2                             supernova-navi_dashboard                             HH-Supernova-Menu-Container                             HH-Supernova-NotificationManager-Container'] [data-qa='login']"

    @property
    def button_sign_in(self):
        # Кнопка "Войти"

        locator = Locator(by=By.CSS_SELECTOR, value=self.SIGNIN_BUTTON_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def button_current_region(self):
        # Кнопка "Ваш текущий регион" на всплывающем окошке
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.BUTTON_REGION_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def authorized_user_icon(self):
        # Иконка авторизованного пользователя
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.USER_ICON_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def input_username(self):
        # Поле для ввода имени пользователя в диалоге авторизации.
        locator = Locator(by=By.CSS_SELECTOR, value=self.USERNAME_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def input_userpassword(self):
        # Поле для ввода пароля пользователя в диалоге авторизации.
        locator = Locator(by=By.CSS_SELECTOR, value=self.USERPASS_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def button_authorize(self):
        # Кнопка "Войти в личный кабинет" в диалоге авторизации.
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.SIGNIN_BUTTON_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    def authorize_hh_user(self, login, password):
        authorized_icon = self.authorized_user_icon
        if (authorized_icon.web_element is None):
            # Мы не авторизованы. Попытаемся авторизоваться.
            if self.button_sign_in.click():
                input_login = self.input_username

                if input_login is not None:
                    input_login.input_text(login)
                else:
                    logger.log_event(
                        """Ошибка.Не найдено поле 'Login' на странице
                        авторизации""")

                input_password = self.input_userpassword
                if input_password is not None:
                    input_password.input_text(password)
                else:
                    logger.log_event("Ошибка. Не найдено поле 'Password'.")

                button_authorize = self.button_authorize
                if button_authorize is not None:
                    if button_authorize.click():
                        logger.log_event("Авторизация успешна.", logging.INFO)
                        return True
                    else:
                        logger.log_event("""Ошибка.
                         Не получилось кликнуть кнопку
                          'Войти в личный кабинет'""")
                else:
                    logger.log_event("""Ошибка.
                    Не получилось кликнуть кнопку
                     'Войти в личный кабинет'""")

            else:
                logger.log_event(
                    "Ошибка. Не получилось кликнуть кнопку 'Войти'")
        else:
            return True

        return False
