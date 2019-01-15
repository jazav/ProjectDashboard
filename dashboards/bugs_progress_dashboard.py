from dashboards.dashboard import AbstractDashboard
import csv
import os.path
import datetime


class BugsProgressDashboard(AbstractDashboard):
    status_list = []
    auto_open, repository = True, None
    bugs_statuses = {'Open': 0, 'In Fix': 0, 'Closed': 0}

    def prepare(self, data):
        self.status_list = data.get_bugs_progress()
        for status in self.status_list:
            self.bugs_statuses[status] += 1
        with open(os.path.abspath('//billing.ru/dfs/incoming/ABryntsev/bugs_progress.csv'), 'a', newline='\n') as csvfile:
            data = csv.writer(csvfile, delimiter=';')
            data.writerow([str(datetime.datetime.now().date())] + list(map(str, self.bugs_statuses.values())))

    def export_to_plotly(self):
        bugs_statuses_progress = {}
        with open(os.path.abspath('//billing.ru/dfs/incoming/ABryntsev/bugs_progress.csv'), 'r', newline='\n') as csvfile:
            data = csv.reader(csvfile, delimiter=';')
            next(data)
            for row in data:
                bugs_statuses_progress[row[0]] = {
                    'Open': row[1],
                    'In Fix': row[2],
                    'Closed': row[3]
                }
            print(bugs_statuses_progress)

    def export_to_plot(self):
        self.export_to_plotly()
