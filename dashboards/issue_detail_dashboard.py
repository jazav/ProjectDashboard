from dashboards.dashboard import AbstractDashboard
from config_controller import *
import pandas as pd
import json
from dashboards.dashboard import *
DELTA_LEN = 42


class IssueDetailDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''

    field_mode = "view"

    def max_key_len(seld, dict):
        key_max_len = 0
        value_max_len = 0

        for key, value in dict.items():
            if key is not None and len(key) >= key_max_len:
                key_max_len = len(key)

            if value is not None and len(str(value)) >= value_max_len:
                value_max_len = len(str(value))

        return key_max_len, value_max_len

    def get_issue_as_str(self):
        fields = self.data.raw['fields']

        key_sz, value_sz = self.max_key_len(fields)
        view_key_sz, view_value_sz = self.max_key_len(self.data.raw['renderedFields'])

        line_str = '-'.ljust(value_sz + view_key_sz + DELTA_LEN, '-') + "\n"

        field_str = self.dashboard_name + ': ' + fields['issuetype']['name'] + ': ' + fields['description'].replace('\n', '') + '\n'

        field_str = field_str + line_str

        if "view" in self.field_mode:
            field_str = field_str + 'Name'.ljust(view_key_sz) + ' | '

        if "tech" in self.field_mode:
            field_str = field_str + 'Tech name'.ljust(key_sz) + ' | '

        if "view" in self.field_mode:
            field_str = field_str + str('Value').ljust(view_value_sz) + ' | '

        if "tech" in self.field_mode:
            field_str = field_str + str('Teach value').ljust(value_sz)

        field_str = field_str + "\n"

        field_str = field_str + line_str

        for field_name in fields:
            if field_name in self.data.raw['names']:
                name = self.data.raw['names'][field_name]
            else:
                name = field_name

            real_value = self.data.raw['fields'][field_name]

            if real_value is not None and isinstance(real_value, str):
                real_value = real_value.replace('\n', '')

            if field_name in self.data.raw['renderedFields'] and real_value != self.data.raw['renderedFields'][field_name]:
                value = self.data.raw['renderedFields'][field_name]
            else:
                value = real_value

            if value is not None and isinstance(value, str):
                value = value.replace('\n', '')

            if "empty" in self.field_mode or ("view" in self.field_mode and value is not None and value != "") or \
                    ("tech" in self.field_mode and real_value is not None and real_value != ""):

                if "view" in self.field_mode:
                    field_str = field_str + name.ljust(view_key_sz) + ' | '

                if "tech" in self.field_mode:
                    field_str = field_str + field_name.ljust(key_sz)  + ' | '

                if "view" in self.field_mode:
                    field_str = field_str + str(value).ljust(view_value_sz) + ' | '

                if "tech" in self.field_mode:
                    field_str = field_str + str(real_value)

                field_str = field_str + "\n"

        field_str = field_str + line_str
        return field_str

    def export_to_txt(self):
        cc = cc_klass()
        path = cc.read_dashboards_config()[FILE_DIR]
        file = path + '/' + self.dashboard_name + '.txt'

        issue_str = self.get_issue_as_str()

        # jira = JIRA(options, basic_auth=(USERNAME, PASSWORD))
        #
        # issue = jira.issue('FOO-100', expand='changelog')
        # changelog = issue.changelog
        #
        # for history in changelog.histories:
        #     for item in history.items:
        #         if item.field == 'status':
        #             print
        #             'Date:' + history.created + ' From:' + item.fromString + ' To:' + item.toString

        f = open(file, 'w')
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
        # df = pd.DataFrame.from_items(data.raw)
        # df.columns = ['movie-id1', 'movie-id2', 'movie-id3', 'movie-id4', 'movie-id5']
        # df['customer_id'] = df.index
        # df = df[['customer_id', 'movie-id1', 'movie-id2', 'movie-id3', 'movie-id4', 'movie-id5']]
        pass

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
