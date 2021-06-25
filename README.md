## Приложение (робот) для массового чтения/записи комментариев на страницах резюме hh.ru

(Несмотря на то, что данная программа успешно эксплуатировалась в 2019 - 2020гг, нет никаких гарантий, что она будет оставаться работоспособной, поскольку сайт hh.ru постоянно эволюционирует - изменяется структура страниц, добавляются способы блокирования роботов и т.п.)

### Требования к окружению:

1. Windows 10 (под другими ОС приложение не тестировалось)
2. Python 3.8
3. Google chrome browser

### Порядок использования:

1. Установить зависимости из файла "Pipfile"
2. Скачать свежую версию Chrome web driver и заменить им файл (уже устаревший) "chromedriver.exe" в составе проекта. Версия драйвера должна соответствовать версии браузера установленного на компьютере
3. Обновить файл с настройками "user_settings_prod.txt". Файл зашифрован алгоритмом Base64. Следует расшифровать файл, обновить настройки и снова зашифровать его. 
4. При необходимости, можно изменить параметры работы программы в файле "config.ini"
5. Запустить файл "main_scenario.py" под отладчиком (например, в VScode)
6. После запуска приложения локально поднимется веб-сервер, который будет ожидать GET-запросы по адресу 127.0.0.1:8000. Сервер способен обрабатывать два типа запросов: запрос на добавление комментария на определенную страничку резюме на сайте hh.ru и запрос на чтение комментариев с определенной странички резюме. Примеры запросов есть в файле "example_queries.txt". В оригинальном сценарии использования запросы поступали от стороннего приложения кадрового учета (код для генерации таких запросов не включен в состав проекта).
7. После получения Get-запроса он автоматически добавляется в БД SQLite (файл "db_hh_data_prod.db") и запускается алгоритм обработки запросов из БД. Программа обращается на сайт hh.ru и открывает страницу для ввода логина и пароля. В этот момент следует остановить процесс под отладчиком (поскольку с определенных пор автоматический логин перестал работать - вероятно, команда hh.ru приняла меры против роботов). Следует вручную залогиниться на сайте hh.ru (и решить капчу, если она появится) и затем продолжить выполнение программы. После этого программа способна обрабатывать  поступившие (и вновь поступающие) запросы на чтение/добавление комментариев автоматически.
8. Программа ходит по страничкам резюме hh.ru и читает/добавляет комментарии в соответствии с полученными командами. При этом до некоторой степени имитируется поведение человека - например, программа делает наравномерные паузы между действиями.
9. Программа отмечает успешно/неуспешно обработанные запросы (команды) в БД.
10. Все полученные с сайта hh.ru комментарии помещаются в файлы в папке "hh_data". Эти комментарии можно потом загрузить в стороннюю программу кадрового учета (код для загрузки комментариев в стороннюю программу в данном проекте отсутствует.)
11. Сведения об ошибках  помещаются в файл "logfile.log".
