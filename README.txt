Краулер
Версия 1.1

Автор: Кихтенко Татьяна (leninanadejda@gmail.com)

Описание
Данное приложение является реализацией веб-краулера, скачивающего страницы. Скачанное можно найти в папке
указанной ключом.
На вход подаются несколько ссылок, каждая из который обрабатывается слудующим образом:
    ● все ссылки из этой страницы скачиваются в указанную директорию
    ● все картинки из этой страницы скачиваются в поддиректорию "pics" указанной папки
    ● текстовое содержимое из этой страницы скачивается в файл entered_dir/page_name.txt

Требования
Python версии не ниже 3.6
Требуемые библиотеки описаны в файле requirements.txt.


Взаимодействие
    -p: ссылки
    -t: количество потоков для обработки
    -f: папка куда скачать html страницы
    --upd: обновляет только что скачанные страницы, если хеш скачанного файла и страницы в интернете различны
    --debug: запуск с ключом, если произошел сбой в программе,
        тогда скачивание начнется с той ссылки, на которой произошел сбой
        в свою очередь, запустив без этого ключа ссылки не будут скачиваться повторно
        благодаря проверке os.path.exists

Примеры запуска:
               py mainc.py
               -p https://www.baristainstitute.com/blog/karoliina-makela/december-2019/successful-coffee-shop-some-basics-behind-business
               -t 2 -f barista_crawl_it

               py mainc.py -p https://www.baristainstitute.com -t 2 -f crawl_downloaded --debug True

                py mainc.py --upd folder_with_files_to update

               py mainc.py
               -p https://www.baristainstitute.com/blog/karoliina-makela/december-2019/successful-coffee-shop-some-basics-behind-business
               -p https://www.baristainstitute.com/recipes/babyccino
               -t 2 -f barista_crawl_it


На модуль web_crawler написаны тесты, их можно найти в test_multicrawler.py.
