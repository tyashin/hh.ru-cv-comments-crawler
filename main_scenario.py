from hh_automation_server import HhAutomationHTTPRequestHandler, Automaton
from random import randint
import logger
import time
from http.server import ThreadingHTTPServer
from threading import Thread
import sqlite3
import sys
import configparser


class MainScenario():
    config = configparser.ConfigParser()
    config.read("config.ini")

    config.read("config.ini")
    MIN_WAIT_AFTER_TASK_COMPLETED = \
        int(config['DEFAULT']['MIN_WAIT_AFTER_TASK_COMPLETED'])
    MAX_WAIT_AFTER_TASK_COMPLETED = \
        int(config['DEFAULT']['MAX_WAIT_AFTER_TASK_COMPLETED'])
    MAX_VISITED_PAGES = \
        int(config['DEFAULT']['MAX_VISITED_PAGES'])

    def __init__(self):
        self.robot = None
        self.conn = None
        self.cursor = None
        self.cursor1 = None
        self.pages_count = 0

    def validate_task(self, cur_task):

        if cur_task.get("command") == "get_comments":
            if (cur_task.get("raw_query") is None) \
                    or (cur_task.get("user") is None) \
                    or (cur_task.get("doc_id") is None) \
                    or (cur_task.get("url") is None):

                return False

        elif cur_task.get("command") == "put_comments":
            if (cur_task.get("raw_query") is None) \
                    or (cur_task.get("user") is None) \
                    or (cur_task.get("doc_id") is None) \
                    or (cur_task.get("comments") is None) \
                    or (not cur_task.get("comments").strip()) \
                    or (cur_task.get("url") is None):

                return False

        else:
            return False

        return True

    def execute_task(self, cur_row=None):
        if cur_row is None:
            return

        if cur_row[1] == "put_comments":
            self.robot.current_task = \
                {"command": cur_row[1], "user": cur_row[2],
                 "doc_id": cur_row[3], "url": cur_row[4],
                 "comments": cur_row[7]}
        elif cur_row[1] == "get_comments":
            self.robot.current_task = {"command": cur_row[1], "user": cur_row[2], "doc_id": cur_row[3], "url": cur_row[4]}

        try:
            if self.robot.execute_command():
                data = (1, cur_row[4], cur_row[1], cur_row[3])
                self.cursor1.execute("UPDATE estaff_commands SET result = ?  WHERE url = ? and command = ? and doc_id = ?", data)
            else:
                data = (2, cur_row[4], cur_row[1], cur_row[3])
                self.cursor1.execute("UPDATE estaff_commands SET result = ? WHERE url = ? and command = ? and doc_id = ?", data)

        except:
            data = (2, cur_row[4], cur_row[1], cur_row[3])
            self.cursor1.execute("UPDATE estaff_commands SET result = ? WHERE url = ? and command = ? and doc_id = ?", data)
        finally:
            self.pages_count += 1
            self.conn.commit()
            time.sleep(randint(self.MIN_WAIT_AFTER_TASK_COMPLETED,
                               self.MAX_WAIT_AFTER_TASK_COMPLETED))

        if self.pages_count == self.MAX_VISITED_PAGES:
            self.robot.hh_resume_page.log_off()
            try:
                self.robot.chrome.close()
                self.robot.chrome.quit()
            except:
                pass

            self.conn.close()
            sys.exit()

    def run(self):
        print('http server is starting...')

        server_address = ('127.0.0.1', 8000)
        httpd = ThreadingHTTPServer(server_address,
                                    HhAutomationHTTPRequestHandler)
        print('http server is running...')

        t1 = Thread(target=httpd.serve_forever)
        t1.start()

        self.robot = Automaton()

        if self.robot.PRODUCTION_ENV:
            self.conn = sqlite3.connect('db_hh_data_prod.db')
        else:
            self.conn = sqlite3.connect('db_hh_data_test.db')

        self.cursor = self.conn.cursor()
        self.cursor1 = self.conn.cursor()

        self.pages_count = 0

        while True:
            time.sleep(1)
            task = self.robot.parse_url()

            while task:
                if not self.validate_task(cur_task=task):
                    logger.log_event("Ошибка.  \
                                Команда не распознана: " + str(task))
                    continue

                query_params = (task["url"], task["command"], task["doc_id"])
                self.cursor.execute("SELECT url from estaff_commands WHERE url = ? and command = ? and doc_id = ?", query_params)
                if self.cursor.fetchone():
                    task = self.robot.parse_url()
                    continue

                task_data = (task["raw_query"], task["command"],
                             task["user"], task["doc_id"],
                             task["url"], task.get("comments"),)


                #self.cursor.execute("INSERT INTO estaff_commands (raw_query, user, doc_id, url, estaff_comments) VALUES(?,?,?,?,?,?);", task_data)

                self.cursor.execute("INSERT INTO estaff_commands VALUES (?,?,?,?,?,0,0,?)", task_data)

                self.conn.commit()

            for row in self.cursor.execute('SELECT * from estaff_commands WHERE number_of_attempts < 1 and result != 1 ORDER BY url'):
                data = (row[5]+1, row[4],  row[1], row[3])
                self.cursor1.execute("UPDATE estaff_commands SET number_of_attempts = ? WHERE url = ? and command = ? and doc_id = ?", data)
                self.conn.commit()

                self.execute_task(cur_row=row)

                if self.robot.check_queue():
                    break


if __name__ == "__main__":
    main_scenario = MainScenario()
    main_scenario.run()
