# Парсер документации Python

## Режимы работы парсера:

 - whats-new
Выводит ссылку на статью "What’s New In Python" редактора, автора последних версий Python
 - latest-versions
Выводит список последних версий Python и их статус
 - download
Скачивает актуальную версию документации
 - pep
Считает количество статусов на всех PEP, сравнивает их значение на главное странице и в карточке PEP


## Опциональные аргументы
####  -h, --help            show this help message and exit
####  -c, --clear-cache     Очистка кеша
####  -o {pretty,file}, --output {pretty,file}


## Установка:
### Склонируйте репозиторий на локальную машину:
`git clone https://github.com/trtobeha/bs4_parser_pep.git`
### Установите виртуальное окружение:
`python3 -m venv venv`
### Активируйте виртуальное окружение:
`venv\Scripts\activate.bat` - для Windows\
`source venv/bin/activate` - для MacOS / Linux
### Установите зависимости:
`pip install -r requirements.txt`
### Запустите парсер:
`python src/main.py [mode]`
