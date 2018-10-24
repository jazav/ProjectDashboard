from jira import JIRA
from adapters.abstract_adapter import AbstractAdapter
from adapters.jsql_builder import JSQLBuilder
from config_controller import *
from jira.resources import Issue
import urllib3
import logging

from adapters.issue_utils import clear_issues

HISTORY_EXPAND = "changelog"
EXPAND_LIST = ['all', 'renderedFields', 'names', 'schema', 'operations', 'editmeta', 'changelog', 'versionedRepresentations']
# renderedFields,names,schema,operations,editmeta,changelog,versionedRepresentations
ALL_IDX = 0
RENDER_FIELDS_IDX = 1
NAMES_IDX = 2
SCHEMA_IDX = 3
OPERATIONS_IDX = 4
EDITMETA_IDX = 5
CHANGELOG_IDX = 6
VERS_REPRESENTATIONS_IDX = 7


def internet_on():
    try:
        http = urllib3.HTTPConnectionPool('www.google.com')
        http.urlopen(url='http://www.google.com', timeout=1.0, method='GET')
        logging.info('network is ON')
        return True
    except urllib3.exceptions.HTTPError as err:
        logging.error('network is OFF')
        return False


class JiraAdapter(AbstractAdapter):

    _connected = False
    _user_name = None
    _password = None
    _servers = None
    _max_results = 0
    _jira = None

    def __init__(self):
        options = JiraAdapter.read_jira_config()
        self._user_name = options['user_name']
        self._password = options['password']
        self._servers = options['servers']
        self._max_results = int(options['max_results'])

    @staticmethod
    def read_jira_config():
        cc = cc_klass()
        options = cc.read_jira_config()

        if options is None:
            options = {'user_name': 'demo.demo',
                       'password': '***',
                       'server': 'https://jira.billing.ru',
                       'max_results': 0,
                       }
        return options

    @staticmethod
    def issues_to_list(issues, clear=True):
        issues_list = []

        if issues is None:
            logging.warning('issues is None')
            return issues_list

        for issue in issues:
            issues_list.append(issue.raw)

        if clear:
            issues_list = clear_issues(issues_list)
        return issues_list

    def _connect(self, url):
        self._connected = False
        if internet_on():
            try:
                self._jira = JIRA(server=url, basic_auth=(self._user_name, self._password))
                self._connected = True

            except Exception as e:
                logging.error("invalid server connection: %s", url)
        else:
            logging.warning('working OFFLINE')
        return self._connected

    def load_by_query(self, query_str, expand, url):
        new_issues = []

        if query_str is None:
            raise ValueError('nothing to load')

        issue_objs = None
        if self._connect(url=url):
            issue_objs = self._jira.search_issues(query_str, maxResults=self._max_results, expand=expand,
                                              json_result=False)

            # for i in range(1,total, 200):
            #  issues.append(jira.search_issues(search_query, maxResults=200, startAt=i))

            new_issues = JiraAdapter.issues_to_list(issue_objs)
            logging.debug('total issues: %s', len(new_issues))

        return new_issues

    def load_by_key(self, key, expand, url):
        if expand is not None:
            expands = expand.split(',') if ',' in expand else [expand]
            for item in expands:
                if item not in EXPAND_LIST:
                    raise ValueError(item + ' is not correct. Valid values: ' + str(EXPAND_LIST))

        issue = None
        if self._connect(url=url):
            try:
                issue = self._jira.issue(key, expand=expand)
                logging.debug('loaded issue %s from %s', issue, self._jira._options['server'])
            except Exception as e:
                logging.error('%s [%s]', e.text, e.status_code)

        return issue

    def get_builder(self):
        return JSQLBuilder()

    def create_issue(self, issues):

        if self._connect():
            issues = self._jira.create_issues(field_list=issues)

        return issues
