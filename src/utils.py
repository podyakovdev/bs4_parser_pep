import logging
import re

import requests_cache
from bs4 import BeautifulSoup
from requests import RequestException

from constants import EXPECTED_STATUS, PEP_URL
from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def logging_deferences(table, table2, list_of_hrefs):
    '''Сравним таблицы и залоггируем отличия'''
    logging.info('Несовпадающие статусы:')
    for i, key in enumerate(table.keys()):
        if table[key] != table2[key]:
            logging.info(
                f'{PEP_URL + list_of_hrefs[i]} '
                f'| Статус в карточке: <{table2[key]}> '
                f'| Статус на главной: <{table[key]}> '
                f'| Ожидаемые статусы: <{EXPECTED_STATUS[table2[key][:1]]}>'
            )


def get_table1(soup):
    '''Получим словарь версия:статус со страницы PEP0.'''
    numerical_section = soup.find('section', {'id': 'numerical-index'})
    section_table = numerical_section.find(
        'table', {'class': 'pep-zero-table docutils align-default'}
    )
    strings = list(section_table.find_all('tr'))
    list_of_versions = []
    for string in strings:
        for i in string:
            version = re.search(r'\>(\d+)\<', str(i))
            if version is not None:
                list_of_versions.append(int(version.groups()[0]))

    # Собираем статусы версий в список
    list_of_abbrs = []
    abbrs = section_table.find_all('abbr')
    for abbr in abbrs:
        list_of_abbrs.append(abbr.text[1:])

    # Словарь (версия:статус)
    table = dict(zip(list_of_versions, list_of_abbrs))
    return table, list_of_versions


def get_table2(soup, list_of_versions):
    '''Получим словарь версия:статус с карточки PEP.'''
    # Соберем ссылки на все версии PEP в список
    list_of_hrefs = []
    numerical_section = soup.find('section', {'id': 'numerical-index'})
    section_table = numerical_section.find(
        'table', {'class': 'pep-zero-table docutils align-default'}
    )
    hrefs = section_table.find_all('a', {'class': 'pep reference internal'})
    for href in hrefs:
        list_of_hrefs.append(href['href'])
    list_of_hrefs = sorted(set(list_of_hrefs))

    #  Пройдемся по ссылкам и соберем статусы оттуда для дальнейшего сравнения
    statuses_from_pages = []
    for href in list_of_hrefs:
        session = requests_cache.CachedSession()
        response = get_response(session, PEP_URL + href)
        soup = BeautifulSoup(response.text, features='lxml')
        section = soup.find('dl', {'class': "rfc2822 field-list simple"})

        pattern = r'\>(?P<status>\w+)\<\/abbr\>\<\/dd\>'
        search = re.search(pattern, str(section))
        if search == '':
            statuses_from_pages.append(' ')
            continue
        statuses_from_pages.append(search.group('status')[:1])
    # Словарь (версия:статус)
    table2 = dict(zip(list_of_versions, statuses_from_pages))
    return table2, list_of_hrefs
