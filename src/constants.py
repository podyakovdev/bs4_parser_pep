from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'

BASE_DIR = Path(__file__).parent

DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'

PEP_URL = 'https://peps.python.org/'

EXPECTED_STATUS = {
        'A': ('Active', 'Accepted'),
        'D': ('Deferred',),
        'F': ('Final',),
        'P': ('Provisional',),
        'R': ('Rejected',),
        'S': ('Superseded',),
        'W': ('Withdrawn',),
        '': ('Draft', 'Active'),
}

WHATS_NEW_RESULTS = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор'), ]

LATEST_VERSIONS_RESULTS = [('Ссылка на документацию', 'Версия', 'Статус')]
LATEST_VERSIONS_PATTERN = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'

PEP_RESULTS = [('Статус', 'Количество')]

DOWNLOAD_FILE_NAME = 'download.html'
