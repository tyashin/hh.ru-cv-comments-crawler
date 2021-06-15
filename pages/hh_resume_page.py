from selenium.webdriver.common.by import By

from pages.base_element import BaseElement
from pages.base_page import BasePage
from pages.locator import Locator
import logger


class HhResumePage(BasePage):

    MORE_COMMENTS_CSS_SELECTOR = \
        "[data-qa='resume-comments'] .bloko-link-switch_tertiary"
    COMMENTS_CSS_SELECTOR = "[data-qa] > [data-qa='resume-comment-item']"
    RESUME_NOT_FOUND_CSS_SELECTOR = ".attention.attention_bad"
    ADD_COMMENT_CSS_SELECTOR = "[data-qa='resume-comments'] .resume-sidebar-link"
    ADD_COMMENT_TEXT_SELECTOR = "Добавить комментарий"
    COMMENT_TEXT_CSS_SELECTOR = ".bloko-textarea_sized-rows"
    SAVE_COMMENT_BTTN_CSS_SELECTOR = ".resume-comment-form [type='submit']"

    CAPTCHA_RAISED = False

    def __init__(self, driver, resume_url):
        super().__init__(driver)
        self.URL = resume_url

    def go(self):
        super().go()
        return self.self_check()

    def self_check(self):

        if self.captcha_warning.web_elements is not None:
            self.CAPTCHA_RAISED = True
            logger.log_event("Captcha. на страничке резюме. "
                             + self.driver.current_url)
            return False

        elif self.resume_not_found_elements().web_elements \
                is not None:

            logger.log_event("Ошибка. Не смогли перейти на страницу резюме "
                             + self.driver.current_url)
            return False

        elif (self.driver.current_url.find("hh.ru/resume/") == -1):
            logger.log_event("Ошибка. Не смогли перейти на страницу резюме "
                             + self.driver.current_url)

            return False

        return True

    def get_comment_items(self):
        # Комментарии в правой части страницы резюме.
        locator = Locator(by=By.CSS_SELECTOR, value=self.COMMENTS_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator,
            single_element=False
        )

    def resume_not_found_elements(self):
        # Ссылка "Нет доступа. Пользователь скрыл или удалил это резюме"
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.RESUME_NOT_FOUND_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator,
            single_element=False
        )

    @property
    def more_comments_link(self):
        # Текст "Еще 3 комментария"
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.MORE_COMMENTS_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def add_comment_link(self):
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.ADD_COMMENT_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def comment_text_area(self):
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.COMMENT_TEXT_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )

    @property
    def save_comment_button(self):
        # Текст "Еще 3 комментария"
        locator = Locator(by=By.CSS_SELECTOR,
                          value=self.SAVE_COMMENT_BTTN_CSS_SELECTOR)
        return BaseElement(
            driver=self.driver,
            locator=locator
        )
