import operator
from config_controller import *
import json
from dashboards.dashboard import *
from datetime import datetime

DELTA_LEN = int(1)
DATE_READ_FORMAT = "%Y-%m-%dT%X.%f%z"
DATE_WRITE_FORMAT = "{0:%Y-%m-%d %X}"

VIEW_MODE = 'public'
TECH_MODE = 'technical'

CREATED_DATE = 0
AUTHOR = 1
FIELD_NAME = 2
FROM_STR = 3
TO_STR = 4

PAGE_WIDTH = 121

SEPARATOR_SIGN = '->'


class IssueDetailDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''

    field_mode = VIEW_MODE

    def is_empty(self, value):
        empty = value is None or value == ""
        if empty:
            return empty

        empty = (type(value) is list) and len(value) == 0

        return empty

    def clear_str(self, str_value):
        if str_value is not None and type(str_value) == str:
             str_value = str_value.replace('\n', '').replace('\t', '').replace('\r', '').strip()
        return str_value

    def get_str_from_dict(self, dct):
        return ''.join(self.get_str_from_list(val) + ', '
                       if type(val) == list else "{!s}={!r}".format(key, val) + ', '
                       for (key, val) in dct.items())[:-2]

    def get_str_from_list(self, lst):
        return ''.join(self.get_str_from_dict(e) + ', '
                       if type(e) is dict else str(e) + ', '
                       for e in lst)[:-2]


    def max_len(self, lst):
        max_len = 0
        for item in lst:
            if item is not None:
                if type(item) == int:
                    item = str(item)

                if type(item) == str:
                    item = self.clear_str(item)

                if type(item) == list:
                    item = self.get_str_from_list(item)

                if type(item) == dict:
                    item = self.get_str_from_dict(item)

                if type(item) in (float, int):
                    item = str(item)

                max_len = max(len(item), max_len)

        return max_len

    def get_header(self):
        title = ''
        if 'description' in self.data.raw['fields'] and self.data.raw['fields']['description'] is not None:
            title = self.data.raw['fields']['summary']
            title = title.strip()

        header_str = self.data._options['server'] + '\n'
        header_str = header_str + 'Key: ' + self.data.key + ' Type: ' + self.data.raw['fields']['issuetype']['name'] + '\n' + \
                     ' ' + title + '\n'
        return header_str

    def prepare_bode(self):
        fields = self.data.raw['fields']

        # sort by field tech name
        fields = sorted(fields.items(), key=operator.itemgetter(0))

        for tech_name, view_value in fields:
            if tech_name in self.data.raw['names']:
                view_name = self.data.raw['names'][tech_name]
            else:
                view_name = tech_name

            view_name = self.clear_str(view_name)

            tech_value = self.data.raw['fields'][tech_name]

    def get_body(self):
        fields = self.data.raw['fields']

        tech_key_sz = self.max_len(list(fields.keys()))
        tech_value_sz = self.max_len(list(fields.values()))

        view_key_sz = self.max_len(list(self.data.raw['names'].values()))
        view_value_sz = self.max_len(list(self.data.raw['renderedFields'].values()))

        line_str = ''

        if VIEW_MODE in self.field_mode:
            line_str = line_str + '-'.ljust(view_key_sz + view_value_sz + 2, '-')

        if TECH_MODE in self.field_mode:
            line_str = line_str + '-'.ljust(tech_key_sz + tech_value_sz + 2, '-')

        line_str = line_str + '-'.ljust(DELTA_LEN, '-') + "\n"

        body_str = line_str

        if VIEW_MODE in self.field_mode:
            body_str = body_str + '|' + 'Name'.ljust(view_key_sz)

        if TECH_MODE in self.field_mode:
            body_str = body_str + '|' + 'Tech name'.ljust(tech_key_sz)

        if VIEW_MODE in self.field_mode:
            body_str = body_str + '|' + 'Value'.ljust(view_value_sz)

        if TECH_MODE in self.field_mode:
            body_str = body_str + '|' + 'Tech value'.ljust(tech_value_sz)

        body_str = body_str + '|' + '\n'

        body_str = body_str + line_str

        # sort by field tech name
        fields = sorted(fields.items(), key=operator.itemgetter(0))

        for field_name, value in fields:
            if field_name in self.data.raw['names']:
                name = self.data.raw['names'][field_name]
            else:
                name = field_name

            name = self.clear_str(name)

            tech_value = value

            if tech_value is not None:
                if isinstance(tech_value, str):
                    tech_value = self.clear_str(tech_value)
                elif isinstance(tech_value, list):
                    tech_value = self.get_str_from_list(tech_value)
                elif isinstance(tech_value, dict):
                    tech_value = self.get_str_from_dict(tech_value)

            if field_name in self.data.raw['renderedFields'] and self.data.raw['renderedFields'][
                field_name] is not None:
                value = self.data.raw['renderedFields'][field_name]


            if value is not None and isinstance(value, str):
                value = self.clear_str(value)

            if "empty" in self.field_mode or (VIEW_MODE in self.field_mode and not self.is_empty(value)) or \
                    (TECH_MODE in self.field_mode and not self.is_empty(tech_value)):

                if VIEW_MODE in self.field_mode:
                    # add name
                    body_str = body_str + '|' + name.ljust(view_key_sz)

                if TECH_MODE in self.field_mode:
                    # add tech name
                    body_str = body_str + '|' + field_name.ljust(tech_key_sz)

                if VIEW_MODE in self.field_mode:
                    # add value
                    body_str = body_str + '|' + str(value).ljust(view_value_sz)

                if TECH_MODE in self.field_mode:
                    # add tech value
                    body_str = body_str + '|' + str(tech_value).ljust(tech_value_sz)

                body_str = body_str + '|' + '\n'

        body_str = body_str + line_str

        return body_str


    def get_body_2(self):
        fields = self.data.raw['fields']

        tech_key_sz = self.max_len(list(fields.keys()))
        tech_value_sz = self.max_len(list(fields.values()))

        view_key_sz = self.max_len(list(self.data.raw['names'].values()))
        view_value_sz = self.max_len(list(self.data.raw['renderedFields'].values()))

        line_str = ''

        if VIEW_MODE in self.field_mode:
            line_str = line_str + '-'.ljust(view_key_sz + view_value_sz + 2, '-')

        if TECH_MODE in self.field_mode:
            line_str = line_str + '-'.ljust(tech_key_sz + tech_value_sz + 2, '-')

        line_str = line_str + '-'.ljust(DELTA_LEN, '-') + "\n"

        body_str = line_str

        if VIEW_MODE in self.field_mode:
            body_str = body_str + '|' + 'Name'.ljust(view_key_sz)

        if TECH_MODE in self.field_mode:
            body_str = body_str + '|' + 'Tech name'.ljust(tech_key_sz)

        if VIEW_MODE in self.field_mode:
            body_str = body_str + '|' + 'Value'.ljust(view_value_sz)

        if TECH_MODE in self.field_mode:
            body_str = body_str + '|' + 'Tech value'.ljust(tech_value_sz)

        body_str = body_str + '|' + '\n'

        body_str = body_str + line_str

        # sort by fielf tech name
        fields = sorted(fields.items(), key=operator.itemgetter(0))

        for field_name, value in fields:
            if field_name in self.data.raw['names']:
                name = self.data.raw['names'][field_name]
            else:
                name = field_name

            name = self.clear_str(name)

            tech_value = self.data.raw['fields'][field_name]

            if tech_value is not None:
                if isinstance(tech_value, str):
                    tech_value = self.clear_str(tech_value)
                elif isinstance(tech_value, list):
                    tech_value = self.get_str_from_list(tech_value)
                elif isinstance(tech_value, dict):
                    tech_value = self.get_str_from_dict(tech_value)

            if field_name in self.data.raw['renderedFields'] and self.data.raw['renderedFields'][
                field_name] is not None:
                value = self.data.raw['renderedFields'][field_name]
            else:
                value = tech_value

            if value is not None and isinstance(value, str):
                value = self.clear_str(value)

            if "empty" in self.field_mode or (VIEW_MODE in self.field_mode and not self.is_empty(value)) or \
                    (TECH_MODE in self.field_mode and not self.is_empty(tech_value)):

                if VIEW_MODE in self.field_mode:
                    # add name
                    body_str = body_str + '|' + name.ljust(view_key_sz)

                if TECH_MODE in self.field_mode:
                    # add tech name
                    body_str = body_str + '|' + field_name.ljust(tech_key_sz)

                if VIEW_MODE in self.field_mode:
                    # add value
                    body_str = body_str + '|' + str(value).ljust(view_value_sz)

                if TECH_MODE in self.field_mode:
                    # add tech value
                    body_str = body_str + '|' + str(tech_value).ljust(tech_value_sz)

                body_str = body_str + '|' + '\n'

        body_str = body_str + line_str

        return body_str

    def prepare_histories_list(self, histories):
        changes_lst = list()

        for history in histories:
            for item in history['items']:
                if item['field'] in self.data.raw['names']:
                    field = self.data.raw['names'][item['field']]
                else:
                    field = item['field']


                change_lst = (DATE_WRITE_FORMAT.format(datetime.strptime(history['created'], DATE_READ_FORMAT)),
                              history['author']['name'],
                              field,
                              '' if item['fromString'] is None else item['fromString'],
                              '' if item['toString'] is None else item['toString'])
                changes_lst.append(change_lst)

        return changes_lst

    def chunks(self, original_str, n):
        """Yield successive n-sized chunks from original_str"""
        end = round(len(original_str)/n)
        if end == 0:
            end = 1
        for i in range(0, len(original_str), end):
            yield original_str[i:i + end]

    def ceil(self, a, b):
        if (b == 0):
            raise Exception("Division By Zero Error!!")  # throw an division by zero error
        if int(a / b) != a / b:
            return int(a / b) + 1
        return int(a / b)

    def format_histories_list(self, lst):

        new_lst = list()
        max_author_len = 0
        max_date_len = 0
        max_field_len = 0
        max_from_len = 0
        max_to_len = 0

        for item in lst:
            if item is not None:
                max_date_len = max(max_date_len, len(item[CREATED_DATE]))
                max_author_len = max(max_author_len, len(item[AUTHOR]))
                max_field_len = max(max_field_len, len(item[FIELD_NAME]))
                max_from_len = max(max_from_len, len(item[FROM_STR]))
                max_to_len = max(max_to_len, len(item[TO_STR]))

        tail = PAGE_WIDTH - (max_date_len + max_author_len + max_field_len + 3)

        if max_from_len > (round(tail/2) - 1) and max_to_len > (round(tail/2) - 1):
            max_from_len = round(tail/2) - 1
            max_to_len = round(tail/2) - 1
        else:
            if max_to_len > max_from_len:
                max_from_len = min(max_from_len, round(tail/2) + 1)
                max_to_len = min(max_to_len, tail - max_from_len - 1)
            else:
                max_to_len = min(max_to_len, round(tail/2) + 1)
                max_from_len = min(max_from_len, tail - max_to_len - 1)

        for item in lst:
            if item is not None:

                from_str = item[FROM_STR]
                to_str = item[TO_STR]

                if len(from_str) > max_from_len:
                    from_count = self.ceil(len(from_str), max_from_len)
                else:
                    from_count = 1

                from_list = list(self.chunks(from_str, from_count))

                len_to = len(to_str)
                if len_to > max_to_len:
                    to_count = self.ceil(len_to, max_to_len)
                else:
                    to_count = 1

                to_list = list(self.chunks(to_str, to_count))

                max_string_count = max(len(from_list), len(to_list))

                for i in range(0, max_string_count):

                    if i == 0:
                        date_str = item[CREATED_DATE]
                        author_str = item[AUTHOR]
                        field_str = item[FIELD_NAME]
                    else:
                        date_str = ''
                        author_str = ''
                        field_str = ''

                    from_str = from_list[i] if len(from_list) > i else ""
                    to_str = to_list[i] if len(to_list) > i else ""

                    new_lst.append((date_str.ljust(max_date_len),
                                    author_str.ljust(max_author_len),
                                    field_str.ljust(max_field_len),
                                    from_str.ljust(max_from_len),
                                    to_str.ljust(max_to_len)))
        return new_lst

    def get_changes_str(self):
        changes_str = 'Changelog:' + '\n'
        changes_str = changes_str + '----------' + '\n'

        changes = self.data.raw['changelog']['histories']
        changes = self.prepare_histories_list(changes)
        changes = self.format_histories_list(changes)

        for item in changes:
            changes_str = changes_str + item[CREATED_DATE] + ' '
            changes_str = changes_str + item[AUTHOR] + ' '
            changes_str = changes_str + item[FIELD_NAME] + ' '
            changes_str = changes_str + item[FROM_STR] + ' '
            changes_str = changes_str + SEPARATOR_SIGN + ' '
            changes_str = changes_str + item[TO_STR] + ' '
            changes_str = changes_str + ' ' + '\n'
        return changes_str

    def get_issue_as_str(self):
        if not (VIEW_MODE in self.field_mode or TECH_MODE in self.field_mode):
            raise EnvironmentError('You should choose either view or tech mode for this dashboard')

        doc_str = self.get_header()
        doc_str = doc_str + self.get_body()
        doc_str = doc_str + '\n'
        doc_str = doc_str + self.get_changes_str()

        return doc_str

    def export_to_txt(self):
        cc = cc_klass()
        path = cc.read_dashboards_config()[FILE_DIR]
        file = path + '/' + self.dashboard_name + '.txt'

        issue_str = self.get_issue_as_str()

        f = open(file, 'w')
        issue_str =issue_str.replace('\u03a3','')
        f.write(issue_str)
        f.close()

    def export_to_json(self):
        cc = cc_klass()
        path = cc.read_dashboards_config()[FILE_DIR]

        file = path + '/' + self.dashboard_name + '.json'

        f = open(file, 'w')
        f.write(json.dumps(self.data.raw))
        f.close()

    def prepare(self, data):
        self.data = data
        return self.data

    def export_to_plot(self):
        self.export_to_file(export_type=EXPORT_MODE[TXT_IDX])

    def export_to_file(self, export_type):
        exports = export_type.split(',') if ',' in export_type else [export_type]

        for item in exports:
            if item == EXPORT_MODE[TXT_IDX]:
                self.export_to_txt()

            if item == EXPORT_MODE[JSON_IDX]:
                self.export_to_json()
