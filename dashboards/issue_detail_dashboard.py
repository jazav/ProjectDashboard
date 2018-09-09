from dashboards.dashboard import AbstractDashboard
from config_controller import *
import pandas as pd
import json

class IssueDetailDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''

    def export_to_file(self):
        cc = cc_klass()
        path = cc.read_dashboards_config()[FILE_DIR]
        file = path + '/' + self.dashboard_name + '.txt'

        f = open(file, 'w')
        f.write(str(self.data.raw))
        f.close()

    def prepare(self, data):
        self.data = data
        #df = pd.DataFrame.from_items(data.raw)
        #df.columns = ['movie-id1', 'movie-id2', 'movie-id3', 'movie-id4', 'movie-id5']
        # df['customer_id'] = df.index
        # df = df[['customer_id', 'movie-id1', 'movie-id2', 'movie-id3', 'movie-id4', 'movie-id5']]
        pass

        return self.data

    def export_to_plot(self):
        self.export_to_file()

    def export_to_json(self):
        cc = cc_klass()
        path = cc.read_dashboards_config()[FILE_DIR]

        file = path + '/' + self.dashboard_name + '.json'

        f = open(file, 'w')
        f.write( json.dumps(self.data.raw))
        f.close()
