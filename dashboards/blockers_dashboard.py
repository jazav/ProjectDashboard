from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta
from adapters.issue_utils import get_domain, get_domain_by_project


class BlockersDashboard(AbstractDashboard):
    auto_open, priority, fixversion, projects = True, None, None, None
