from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain, get_domain_by_project


class AllBugsDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    bssbox_dict, domain_dict = {'all': {'open': 0, 'in fix': 0, 'resolved': 0, 'closed': 0}},\
                               {'all': {'open': 0, 'in fix': 0, 'resolved': 0, 'closed': 0}}

    def prepare(self, data):
        for project, component, status in zip(data['project'], data['component'], data['status']):
            if project != 'BSSBOX':
                domain = get_domain_by_project(project)
                if domain not in self.domain_dict.keys():
                    self.domain_dict[domain] = {'open': 0, 'in fix': 0, 'resolved': 0, 'closed': 0}
                self.domain_dict[domain][status] += 1
                self.domain_dict['all'][status] += 1
            else:
                pass

    def export_to_plotly(self):
        pass

    def export_to_plot(self):
        self.export_to_plotly()
