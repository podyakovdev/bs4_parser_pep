import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOAD_FILE_NAME, LATEST_VERSIONS_PATTERN,
                       LATEST_VERSIONS_RESULTS, MAIN_DOC_URL, PEP_RESULTS,
                       PEP_URL, WHATS_NEW_RESULTS)
from outputs import control_output
from utils import (find_tag, get_response, get_table1, get_table2,
                   logging_deferences)


def whats_new(session):

    WHATS_NEW_URL = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, WHATS_NEW_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = WHATS_NEW_RESULTS[:]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(WHATS_NEW_URL, version_a_tag['href'])
        response = session.get(version_link)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = soup.find('h1')
        dl = soup.find('dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text),
        )
    return results


def latest_versions(session):

    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return

    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = find_tag(soup, 'div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' not in ul.text:
            raise Exception('Не найден список c версиями Python')
        a_tags = ul.find_all('a')

    results = LATEST_VERSIONS_RESULTS[:]
    pattern = LATEST_VERSIONS_PATTERN
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):

    downloads_url = urljoin(MAIN_DOC_URL, DOWNLOAD_FILE_NAME)
    response = get_response(session, downloads_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']

    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):

    response = get_response(session, PEP_URL)
    if response is None:
        return

    # Соберем статусы с главной страницы:
    soup = BeautifulSoup(response.text, features='lxml')
    table, list_of_versions = get_table1(soup)
    table2, list_of_hrefs = get_table2(soup, list_of_versions)

    # Сохраним необходимые строки для csv:
    results = PEP_RESULTS[:]
    for status in tqdm(set(table2.values())):
        count = list(table2.values()).count(status)
        results.append(
            (status, count)
        )
    results.append(
        ('Total', len(table2.keys()))
    )

    # Залоггируем различающиеся статусы:
    logging_deferences(table, table2, list_of_hrefs)
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():

    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')

    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()

    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)

    if results is not None:
        control_output(results, args)

    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
