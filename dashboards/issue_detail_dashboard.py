from dashboards.dashboard import AbstractDashboard
from config_controller import *
import pandas as pd
import json
from dashboards.dashboard import *


class IssueDetailDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''

    def export_to_txt(self):
        cc = cc_klass()
        path = cc.read_dashboards_config()[FILE_DIR]
        file = path + '/' + self.dashboard_name + '.txt'

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
        f.write(str(self.data))
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
