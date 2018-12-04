from dashboards.dashboard import AbstractDashboard


class ArbaIssuesDashboard(AbstractDashboard):
    name_list, assignee_list, created_list, duedate_list = [], [], [], []
    auto_open, assignees = True, None
    team_dict = {}

    def prepare(self, data):
        self.name_list, self.assignee_list, self.created_list, self.duedate_list = data.get_arba_issues(self.assignees)

        for i in range(len(self.name_list)):
            print(self.name_list[i])
