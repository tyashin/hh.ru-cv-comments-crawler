import sys
import logging

logging.basicConfig(filename="logfile.log",
                    format="%(asctime)s %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                    level=logging.INFO)


def log_event(msg="", level=logging.ERROR, exit=False):

    if level == logging.ERROR:
        logging.error(msg)
    else:
        logging.info(msg)

    if exit:
        sys.exit("Ошибка. Подробности см. в лог-файле")
