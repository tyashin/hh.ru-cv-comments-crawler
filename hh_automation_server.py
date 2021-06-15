import os
import settings_manager
import logger
import sys
import time
import configparser
from http.server import BaseHTTPRequestHandler
from queue import Queue
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.parse import unquote
from pages.hh_main_page import HhMainPage
from pages.hh_resume_page import HhResumePage
from chrome import Chrome
from pages.base_element import BaseElement
from random import randint

request_queue = Queue()


class HhAutomationHTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        self.send_response(200)
        self.send_header('Content-type', 'text-html')
        self.end_headers()

        request_queue.put(self.path)

        return


class Automaton():
    config = configparser.ConfigParser()
    config.read("config.ini")
    MIN_WAIT_AFTER_TASK_COMPLETED = \
        int(config['DEFAULT']['MIN_WAIT_AFTER_TASK_COMPLETED'])

    SHARED_DIR = \
        config['DEFAULT']['SHARED_DIR']
    MAX_LINK_CLICK_COUNT = \
        int(config['DEFAULT']['MAX_LINK_CLICK_COUNT'])
    PRODUCTION_ENV = \
        bool(config['DEFAULT']['PRODUCTION_ENV'])

    def __init__(self):
        self.chrome = None
        self.hh_username = None
        self.hh_password = None
        self.estaff_user_xml = None
        self.main_page = None
        self.hh_resume_page = None
        self.current_task = {}
        self.current_user = None
        self.current_url = None
        self.current_comments = None

    def check_queue(self):
        return not request_queue.empty()

    def parse_url(self):

        if request_queue.empty():
            return None

        raw_path = request_queue.get()
        parsed_url = urlparse(raw_path)
        cur_command = parsed_url.path.replace("/", "").strip()
        cur_query = parsed_url.query.strip()
        cur_path = raw_path.replace("/", "", 1) \
            .strip().lower().replace(" ", "")

        if not cur_command or not cur_query:
            return None

        command_n_params = \
            dict(element.split("=") for element in cur_query.split("&"))

        command_n_params["raw_query"] = cur_path
        command_n_params["command"] = cur_command

        return command_n_params

    def execute_command(self):
        if (not self.current_task["command"]):
            return False

        if self.current_task["command"] == "put_comments":
            return self.put_comments_to_hh()
        elif self.current_task["command"] == "get_comments":
            return self.get_comments_from_hh()

    def check_authorization_at_hh(self):
        if self.main_page is None:
            self.main_page = HhMainPage(driver=self.chrome.browser)
            self.main_page.go()

            self.imitate_humans_delay()
            self.main_page.button_current_region.click()
            self.imitate_humans_delay()

        if (not self.main_page.authorize_hh_user(login=self.hh_username,
                                                 password=self.hh_password)):
            logger. \
                log_event("Ошибка. Не удалось авторизоваться на сайте hh.ru.")
            return False

        return True

    def init_and_authorize(self):
        if (not self.current_task["url"]):
            return False

        if not self.get_credentials():
            return False

        if not self.initialize_browser():
            return False

        self.current_user = self.current_task["user"]

        if not self.check_authorization_at_hh():
            return False

        return True

    def goto_resume_page(self):

        r_url = "https://hh.ru/resume/" + self.current_task["url"]

        if (self.hh_resume_page is None) or (self.current_url != r_url):
            self.hh_resume_page = HhResumePage(resume_url=r_url,
                                               driver=self.chrome.browser)
            if not self.hh_resume_page.go():
                if self.hh_resume_page.CAPTCHA_RAISED:
                    logger.log_event("Замечена Captcha. Завершаем программу. ")
                    try:
                        self.chrome.close()
                        self.chrome.browser.quit()
                        sys.exit()
                    except:
                        sys.exit()
                else:
                    return False

        self.current_url = r_url
        return True

    def imitate_humans_delay(self,
                             min_delay=BaseElement.MIN_WAIT_SEC,
                             max_delay=BaseElement.USUAL_WAIT_SEC):

        time.sleep(randint(min_delay, max_delay))

    def put_comments_to_hh(self):

        comments_str = unquote(self.current_task["comments"]).strip()

        if not comments_str:
            return False

        if not self.init_and_authorize():
            return False

        self.imitate_humans_delay()

        if not self.goto_resume_page():
            return False

        self.imitate_humans_delay()

        # Проверим, что на странице уже нет комментария
        # с таким же текстом, добавленного вручную
        search_string = comments_str.split("\n", 1)[1]
        click_count = 0
        while (self.hh_resume_page.more_comments_link.click()) \
                and (click_count < self.MAX_LINK_CLICK_COUNT):
            click_count += 1
            self.imitate_humans_delay()
            continue

        comment_elements = self.hh_resume_page.get_comment_items().web_elements
        if (comment_elements):
            for comment_element in comment_elements:
                try:
                    elements_array = comment_element.text.strip().split("\n")

                    if (search_string == elements_array[0].strip()) \
                            or (comments_str == elements_array[0].strip()):
                        return False
                except:
                    break

        if not self.hh_resume_page.add_comment_link.click():
            logger.log_event("Ошибка. Не удалось " +
                             "кликнуть кнопку добавления " +
                             "комментария на странице резюме " +
                             self.current_task["url"])

            return False

        self.imitate_humans_delay()

        if not self.hh_resume_page.comment_text_area:
            logger.log_event("Ошибка. Не найдено поле " +
                             "для записи комментария " +
                             "на странице резюме " +
                             self.current_task["url"])

            return False

        if not \
            self.hh_resume_page.comment_text_area. \
                input_text(comments_str):

            logger.log_event("Ошибка. Не удалось " +
                             "поместить текст комментария " +
                             "в текстовое поле на странице резюме " +
                             self.current_task["url"])

            return False

        self.imitate_humans_delay()

        if not self.hh_resume_page.save_comment_button.click():
            logger.log_event("Ошибка. Не удалось кликнуть " +
                             "кнопку сохранения " +
                             "комментария на странице резюме " +
                             self.current_task["url"])

            return False

        return True

    def get_comments_from_hh(self):

        if not self.init_and_authorize():
            return False

        self.imitate_humans_delay()

        if not self.goto_resume_page():
            return False

        click_count = 0
        while (self.hh_resume_page.more_comments_link.click()) \
                and (click_count < self.MAX_LINK_CLICK_COUNT):
            click_count += 1
            self.imitate_humans_delay()
            continue

        comment_elements = self.hh_resume_page.get_comment_items().web_elements
        response_string = ""

        if (comment_elements):
            for comment_element in comment_elements:
                try:
                    elements_array = comment_element.text.strip().split("\n")

                    if ("(ES," in elements_array[0]) \
                            or (not elements_array[0].strip()):
                        continue  # этот коммент был ранее загружен из E-staff

                    response_string = response_string \
                        + "Пользователь: {}, Комментарий:{} ". \
                        format(elements_array[1], elements_array[0]) + "\n"
                except:
                    logger.log_event("Ошибка при получении комментариев "
                                     + "со страницы резюме "
                                     + self.current_task["url"])
                    return False

        if not response_string.strip():
            return False

        response_string = "Комментарии получены" \
            + " со страницы https://hh.ru/resume/" \
            + self.current_task["url"] + "  роботом  " \
            + datetime.today().strftime('%d-%m-%Y') \
            + ". " + "\n\n\n" + response_string

        try:
            settings_manager. \
                write_data_to_file(str.encode(response_string,
                                   'UTF-8'), self.generate_file_name())
     
            return True
        except:
            logger.log_event("Ошибка при записи файла"
                             + " комментариев со страницы резюме "
                             + self.current_task["url"])

            return False

    def generate_file_name(self):
        return os.path.join(os.path.normpath(self.SHARED_DIR),
                            self.current_task["command"] + "_"
                            + self.current_task["doc_id"])


    def get_credentials(self):

        if (self.current_user == self.current_task["user"]) \
                and (self.estaff_user_xml is not None):
            return True

        if self.PRODUCTION_ENV:
            user_prefs = \
                settings_manager \
                .read_settings_from_file("user_settings_prod.txt")
        else:
            user_prefs = settings_manager \
                .read_settings_from_file("user_settings_test.txt")

        soup = BeautifulSoup(user_prefs, 'lxml')
        self.estaff_user_xml = soup.find("estaff_username",
                                         string=self.current_task["user"])

        if self.estaff_user_xml is None:
            logger.log_event("Ошибка.  \
                             Не найдены настройки пользователя E-staff "
                             + self.current_task["user"])
            return False

        self.hh_username = self.estaff_user_xml. \
            parent.hh_username.string.strip()
        self.hh_password = self.estaff_user_xml. \
            parent.hh_password.string.strip()

        return True

    def initialize_browser(self):

        if (self.current_user == self.current_task["user"]) \
                and (self.chrome is not None) \
                and (self.chrome.get_status()):
            return True

        if self.estaff_user_xml is None:
            return False

        try:
            self.chrome = Chrome(driver='chromedriver',
                                 browser_options=[opt.string for
                                                  opt in self.estaff_user_xml.
                                                  parent.chrome_options if
                                                  opt.string.strip() != ""])
            self.main_page = None
            self.hh_resume_page = None
        except:
            return False

        return True
