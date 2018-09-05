import math
from datetime import datetime
import numpy as np
import pandas as pd
import pytz


def nat_check(nat):
    return nat is None or nat == np.datetime64('NaT') or nat is pd.NaT or (
            isinstance(nat, (int, float)) and math.isnan(nat))


def get_domain(component):
    return {
        'Analytics': 'ARBA',
        'Architecture': 'ARBA',
        'B2C Self-service': 'DFE',
        'BFAM': 'Billing',
        'Billing': 'Billing',
        'CES': 'Billing',
        'CRM': 'CRM',
        'CRM Processes': 'CRM',
        'Case management': 'CRM',
        'Case Management': 'CRM',
        'Collection': 'Billing',
        'CustomerOrder': 'Ordering',
        'DFE': 'DFE',
        'Fin account': 'Billing',
        'Interactions': 'CRM',
        'Inventory': 'Billing',
        'Marketplace': 'CRM',
        'Notification': 'Infra',
        'Party Management': 'CRM',
        'Payments': 'Billing',
        'Pays': 'Billing',
        'Processes': 'CRM',
        'Product Instances': 'CRM',
        'Product Processes': 'CRM',
        'ProductProcess': 'CRM',
        'Report Engine': 'Infra',
        'SSO': 'Infra',
        'Searching': 'CRM',
        'Security': 'Infra',
        'configuration': 'Component Architecture',
        'logical inventory': 'CRM',
        'notification_managment': 'Infra',
        'oredring': 'Ordering',
        'payment': 'Billing',
        'report engine': 'Infra',
        'service activator': 'Component Architecture',

        None: None
    }[component]


def clear_issues(issues):
    for issue in issues:
        issue_keys = list(issue.keys())
        for issue_key in issue_keys:
            if isinstance(issue[issue_key], (dict)):
                # below are properties of Fields
                field_keys = list(issue[issue_key].keys())

                for field_key in field_keys:
                    if issue[issue_key][field_key] is None or \
                            ("components" not in field_key and
                             "assignee" not in field_key and
                             "progress" not in field_key and
                             "reporter" not in field_key and
                             "issuetype" not in field_key and
                             "aggregateprogress" not in field_key and
                             "project" not in field_key and
                             "status" not in field_key and
                             "creator" not in field_key and
                             "resolution" not in field_key and
                             "customfield" not in field_key and
                             "created" not in field_key and
                             "updated" not in field_key and
                             "summary" not in field_key and
                             "description" not in field_key and
                             "timeoriginalestimate" not in field_key and
                             "duedate" not in field_key and
                             "resolutiondate" not in field_key and
                             "components" not in field_key and
                             "timeestimate" not in field_key and
                             "timespent" not in field_key and
                             "subtasks" not in field_key and
                             "issuelinks" not in field_key and
                             "parent" not in field_key and
                             "priority" not in field_key and
                             "resolution" not in field_key

                            ):
                        del issue[issue_key][field_key]
            else:
                # property of level 1
                if issue_key not in ('key', 'id') or issue[issue_key] is None:
                    del issue[issue_key]

    return issues


ID_FIELD = 'id'
KEY_FIELD = 'key'
FIELDS_FIELD = 'fields'
NAME_FIELD = 'name'
CREATOR_FIELD = 'creator'
DUEDATE_FIELD = 'duedate'
RESOLUTIONDATE_FIELD = 'resolutiondate'
RESOLUTION_FIELD = 'resolution'
ASSIGNEE_FIELD = 'assignee'
EPICLINK_FIELD = 'customfield_10201'
LABEL_FIELD = 'customfield_11100'
UPDATED_FIELD = 'updated'
CREATED_FIELD = 'created'
PROJECT_FIELD = 'project'
TYPE_FIELD = 'issuetype'
STATUS_FIELD = 'status'
COMPONENTS_FIELD = 'components'
TIMEORIGINALESTIMATE_FIELD = 'timeoriginalestimate'
TIMEESTIMATE_FIELD = 'timeestimate'
TIMESPENT_FIELD = 'timespent'
AGGREGATETIMEESTIMATE_FIELD = 'aggregatetimeestimate'
AGGREGATETIMEORIGINALESTIMATE_FIELD = 'aggregatetimeoriginalestimate'
SUBTASKS_FIELD = 'subtasks'
SUMMARY_FIELD = 'summary'
DESCRIPTION_FIELD = 'description'
PARENT_FIELD = 'parent'
ISSUELINKS_FIELD = 'issuelinks'
REPORTER_FIELD = 'reporter'
PRIORITY_FIELD = 'priority'
AGGREGATEPROGRESS_FIELD = 'aggregateprogress'
PROGRESS_FIELD = 'progress'
STORYPOINTS_FIELD = 'customfield_10208'

DATETIME_WRITE_FORMAT = "{0:%Y-%m-%d %X.%f%z}"
DATETIME_READ_FORMAT = "%Y-%m-%d %X.%f%z"
DATE_WRITE_FORMAT = '{0:%Y-%m-%d}'

DATETIME_FORMAT = '%Y-%m-%dT%X.%f%z'
DATE_FORMAT = '%Y-%m-%d'


def issues_to_dict(issues):
    issue_dict = dict()

    if issues is None or len(issues) == 0:
        return issue_dict

    for issue in issues:

        id = int(issue[ID_FIELD])
        key = issue[KEY_FIELD]

        if CREATOR_FIELD in issue[FIELDS_FIELD]:
            creator = issue[FIELDS_FIELD][CREATOR_FIELD][NAME_FIELD]
        else:
            creator = ''

        if ASSIGNEE_FIELD in issue[FIELDS_FIELD]:
            assignee = issue[FIELDS_FIELD][ASSIGNEE_FIELD][NAME_FIELD]
        else:
            assignee = ''

        if REPORTER_FIELD in issue[FIELDS_FIELD]:
            reporter = issue[FIELDS_FIELD][REPORTER_FIELD][NAME_FIELD]
        else:
            reporter = ''

        if RESOLUTIONDATE_FIELD in issue[FIELDS_FIELD]:
            resolutiondate = datetime.strptime(issue[FIELDS_FIELD][RESOLUTIONDATE_FIELD], DATETIME_FORMAT)
        else:
            resolutiondate = None

        if RESOLUTION_FIELD in issue[FIELDS_FIELD]:
            resolution = issue[FIELDS_FIELD][RESOLUTION_FIELD][NAME_FIELD]
        else:
            resolution = ''

        if DUEDATE_FIELD in issue[FIELDS_FIELD]:

            duedate = datetime.strptime(issue[FIELDS_FIELD][DUEDATE_FIELD], DATE_FORMAT)
            # it's timezone unaware

            duedate = pytz.utc.localize(duedate)
            # noew it's TZ aware
        else:
            duedate = None

        if UPDATED_FIELD in issue[FIELDS_FIELD]:
            updated = datetime.strptime(issue[FIELDS_FIELD][UPDATED_FIELD], DATETIME_FORMAT)
        else:
            updated = None

        if CREATED_FIELD in issue[FIELDS_FIELD]:
            created = datetime.strptime(issue[FIELDS_FIELD][CREATED_FIELD], DATETIME_FORMAT)
        else:
            created = None

        if PROJECT_FIELD in issue[FIELDS_FIELD]:
            project = issue[FIELDS_FIELD][PROJECT_FIELD][KEY_FIELD]
        else:
            project = ''

        if PARENT_FIELD in issue[FIELDS_FIELD]:
            parent = issue[FIELDS_FIELD][PARENT_FIELD][KEY_FIELD]
        else:
            parent = ''

        if TYPE_FIELD in issue[FIELDS_FIELD]:
            issuetype = issue[FIELDS_FIELD][TYPE_FIELD][NAME_FIELD]
        else:
            issuetype = ''

        if STATUS_FIELD in issue[FIELDS_FIELD]:
            status = issue[FIELDS_FIELD][STATUS_FIELD][NAME_FIELD]
        else:
            status = ''

        if COMPONENTS_FIELD in issue[FIELDS_FIELD]:
            components = ''
            lenght = len(issue[FIELDS_FIELD][COMPONENTS_FIELD])
            for i in range(lenght):
                components = components + issue[FIELDS_FIELD][COMPONENTS_FIELD][i][NAME_FIELD]
                if i < lenght - 1:
                    components = components + ','
        else:
            components = ''

        if ISSUELINKS_FIELD in issue[FIELDS_FIELD]:
            outwards = ''
            inwards = ''
            lenght = len(issue[FIELDS_FIELD][ISSUELINKS_FIELD])
            for i in range(lenght):
                if 'outwardIssue' in issue[FIELDS_FIELD][ISSUELINKS_FIELD][i]:
                    if len(outwards) > 0:
                        outwards = outwards + ','
                    outwards = outwards + issue[FIELDS_FIELD][ISSUELINKS_FIELD][i]['outwardIssue'][KEY_FIELD]
                else:
                    if len(inwards) > 0:
                        inwards = inwards + ','
                    inwards = inwards + issue[FIELDS_FIELD][ISSUELINKS_FIELD][i]['inwardIssue'][KEY_FIELD]
        else:
            outwards = ''
            inwards = ''

        if PRIORITY_FIELD in issue[FIELDS_FIELD]:
            priority = issue[FIELDS_FIELD][PRIORITY_FIELD][NAME_FIELD]
        else:
            priority = ''

        if LABEL_FIELD in issue[FIELDS_FIELD]:
            labels = ','.join(issue[FIELDS_FIELD][LABEL_FIELD])
        else:
            labels = ''

        if SUBTASKS_FIELD in issue[FIELDS_FIELD]:
            subtasks = ''
            lenght = len(issue[FIELDS_FIELD][SUBTASKS_FIELD])
            for i in range(lenght):
                subtasks = subtasks + issue[FIELDS_FIELD][SUBTASKS_FIELD][i][KEY_FIELD]
                if i < lenght - 1:
                    subtasks = subtasks + ','
        else:
            subtasks = ''

        if TIMEORIGINALESTIMATE_FIELD in issue[FIELDS_FIELD]:
            timeoriginalestimate = float(issue[FIELDS_FIELD][TIMEORIGINALESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
        else:
            timeoriginalestimate = 0.00

        if STORYPOINTS_FIELD in issue[FIELDS_FIELD]:
            storypoints = float(issue[FIELDS_FIELD][STORYPOINTS_FIELD])
        else:
            storypoints = 0.00

        if EPICLINK_FIELD in issue[FIELDS_FIELD]:
            epiclink = issue[FIELDS_FIELD][EPICLINK_FIELD]
        else:
            epiclink = ''

        if TIMEESTIMATE_FIELD in issue[FIELDS_FIELD]:
            timeestimate = issue[FIELDS_FIELD][TIMEESTIMATE_FIELD] / 60 / 60 / 8  # sec->man-days
        else:
            timeestimate = 0.00

        if TIMESPENT_FIELD in issue[FIELDS_FIELD]:
            timespent = float(issue[FIELDS_FIELD][TIMESPENT_FIELD] / 60 / 60 / 8)  # sec->man-days
        else:
            timespent = 0.00

        if AGGREGATETIMEESTIMATE_FIELD in issue[FIELDS_FIELD]:
            aggregatetimeestimate = float(
                issue[FIELDS_FIELD][AGGREGATETIMEESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
        else:
            aggregatetimeestimate = 0.00

        if AGGREGATEPROGRESS_FIELD in issue[FIELDS_FIELD] and 'percent' in issue[FIELDS_FIELD][AGGREGATEPROGRESS_FIELD]:
            aggregateprogress = float(issue[FIELDS_FIELD][AGGREGATEPROGRESS_FIELD]['percent'])
        else:
            aggregateprogress = 0.00

        if PROGRESS_FIELD in issue[FIELDS_FIELD] and 'percent' in issue[FIELDS_FIELD][PROGRESS_FIELD]:
            progress = float(issue[FIELDS_FIELD][PROGRESS_FIELD]['percent'])
        else:
            progress = 0.00

        if AGGREGATETIMEORIGINALESTIMATE_FIELD in issue[FIELDS_FIELD]:
            aggregatetimeoriginalestimate = float(issue[FIELDS_FIELD][
                                                      AGGREGATETIMEORIGINALESTIMATE_FIELD] / 60 / 60 / 8)  # sec->man-days
        else:
            aggregatetimeoriginalestimate = 0.00

        if SUMMARY_FIELD in issue[FIELDS_FIELD]:
            summary = issue[FIELDS_FIELD][SUMMARY_FIELD]
        else:
            summary = ''

        if DESCRIPTION_FIELD in issue[FIELDS_FIELD]:
            description = issue[FIELDS_FIELD][DESCRIPTION_FIELD]
        else:
            description = ''

        issue = {
            KEY_FIELD: key,
            TYPE_FIELD: issuetype,
            STATUS_FIELD: status,
            PROJECT_FIELD: project,
            COMPONENTS_FIELD: components,
            'labels': labels,
            'epiclink': epiclink,
            PARENT_FIELD: parent,
            SUBTASKS_FIELD: subtasks,
            'outwards': outwards,
            'inwards': inwards,
            SUMMARY_FIELD: summary,
            DESCRIPTION_FIELD: description,
            RESOLUTION_FIELD: resolution,
            RESOLUTIONDATE_FIELD: resolutiondate,
            TIMEORIGINALESTIMATE_FIELD: timeoriginalestimate,
            TIMEESTIMATE_FIELD: timeestimate,
            TIMESPENT_FIELD: timespent,
            'storypoints': storypoints,
            CREATOR_FIELD: creator,
            ASSIGNEE_FIELD: assignee,
            REPORTER_FIELD: reporter,
            DUEDATE_FIELD: duedate,
            AGGREGATETIMEESTIMATE_FIELD: aggregatetimeestimate,
            AGGREGATETIMEORIGINALESTIMATE_FIELD: aggregatetimeoriginalestimate,
            UPDATED_FIELD: updated,
            CREATED_FIELD: created,
            PROGRESS_FIELD: progress,
            AGGREGATEPROGRESS_FIELD: aggregateprogress,
            PRIORITY_FIELD: priority,
            ID_FIELD: id}

        issue_dict[key] = issue

    return issue_dict


def serialize(issue_dict):
    for issue in issue_dict.values():
        if nat_check(issue[RESOLUTIONDATE_FIELD]):

            issue[RESOLUTIONDATE_FIELD] = None
        else:
            issue[RESOLUTIONDATE_FIELD] = DATETIME_WRITE_FORMAT.format(issue[RESOLUTIONDATE_FIELD])

        if nat_check(issue[DUEDATE_FIELD]):
            issue[DUEDATE_FIELD] = None
        else:
            issue[DUEDATE_FIELD] = DATETIME_WRITE_FORMAT.format(issue[DUEDATE_FIELD])

        if nat_check(issue[UPDATED_FIELD]):
            issue[UPDATED_FIELD] = None
        else:
            issue[UPDATED_FIELD] = DATETIME_WRITE_FORMAT.format(issue[UPDATED_FIELD])

        if nat_check(issue[CREATED_FIELD]):
            issue[CREATED_FIELD] = None
        else:
            issue[CREATED_FIELD] = DATETIME_WRITE_FORMAT.format(issue[CREATED_FIELD])

        #
        # if something is missed, we are trying to cast datetime fields
        #

        for k, v in issue.items():
            if type(v) == datetime:
                if nat_check(v):
                    issue[k] = None
                else:
                    issue[k] = DATETIME_WRITE_FORMAT.format(v)
    return issue_dict


def deserialize(issue_dict):
    if issue_dict is not None and len(issue_dict) > 0:
        for issue in issue_dict.values():

            if issue[RESOLUTIONDATE_FIELD] is not None:
                issue[RESOLUTIONDATE_FIELD] = datetime.strptime(issue[RESOLUTIONDATE_FIELD], DATETIME_READ_FORMAT)

            if issue[DUEDATE_FIELD] is not None:
                issue[DUEDATE_FIELD] = datetime.strptime(issue[DUEDATE_FIELD], DATETIME_READ_FORMAT)
                # DATE_FORMAT

            if issue[UPDATED_FIELD] is not None:
                issue[UPDATED_FIELD] = datetime.strptime(issue[UPDATED_FIELD], DATETIME_READ_FORMAT)

            if issue[CREATED_FIELD] is not None:
                issue[CREATED_FIELD] = datetime.strptime(issue[CREATED_FIELD], DATETIME_READ_FORMAT)
    return issue_dict


def merge_issue(issue_dict, updated_issue_dict):
    if updated_issue_dict is not None and len(updated_issue_dict) > 0:
        if issue_dict is None or len(issue_dict) == 0:
            issue_dict = updated_issue_dict
        else:
            for key, value in updated_issue_dict.items():
                issue_dict[key] = value
    return issue_dict


def get_data_frame(issue_dict):
    df = pd.DataFrame.from_dict(issue_dict, orient='index')
    return df
