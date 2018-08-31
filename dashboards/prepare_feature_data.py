import logging
import re

import pandas as pd
from pylab import *

TOTAL_NAME = 'Total:'


def unique(list1):
    x = np.array(list1)
    return np.unique(x)


def calc_fact_estimates(plan_df, all_data_df):
    for row in plan_df.itertuples():
        fact_data = pd.DataFrame()

    return fact_data


def list_from_string(source_str, reg_filter_list, del_substring):
    lst = list()
    substrings = source_str.split(',')
    for substring in substrings:
        for reg_filter in reg_filter_list:
            if re.search(reg_filter, substring):
                if del_substring is not None:
                    lst.append(substring.replace(del_substring, 'F-'))
                else:
                    lst.append(substring)
    return lst


def get_feature_list(data_dict):
    fl = list()
    for k, v in data_dict.items():
        fl.append(list_from_string(source_str=v, reg_filter_list={'num\d'}, del_substring='num'))
    fl = unique(fl)

    logging.debug('count of features: %s', len(fl))
    return fl


def get_group_list(data_dict):
    fl = list()
    for k, v in data_dict.items():
        fl.append(list_from_string(source_str=v, reg_filter_list={'\d'}, del_substring='num'))
    fl = unique(fl)
    return fl


def get_feature_series(data_lst, char_cnt):
    fgl = list()

    for item in data_lst:
        fgl.append(item[:-char_cnt])

    fgl = unique(fgl)

    logging.debug('count of feature group: %s', len(fgl))
    return fgl


def applying_OR_filter(issue_df, or_filter_list):
    or_issue_df = None
    if or_filter_list is None:
        or_issue_df = issue_df
    for or_filter in or_filter_list:
        tmp_df = issue_df[issue_df["labels"].str.contains(or_filter)]
        if or_issue_df is None or len(or_issue_df) == 0:
            or_issue_df = tmp_df
        else:
            or_issue_df = or_issue_df.append(tmp_df)

        if len(tmp_df) == 0:
            logging.warning("No data for dashboard: %s", or_filter)

    return or_issue_df


def applying_AND_filter(issue_df, and_filter_list):
    and_issue_df = None
    if and_filter_list is None:
        and_issue_df = issue_df
    else:
        for and_filter in and_filter_list:
            tmp_df = issue_df[issue_df["labels"].str.contains(and_filter)]

            if and_issue_df is None or len(and_issue_df) == 0:
                and_issue_df = tmp_df
            else:
                and_issue_df = and_issue_df.append(tmp_df)

        if len(issue_df) == 0:
            logging.warning("No data for dashboard: %s", and_filter)

    return and_issue_df


def get_fact_data(epic_df, issue_df):
    sum_series = issue_df.groupby(['epiclink'])['timeoriginalestimate'].sum()
    # if we ned data frame
    # epic_df = epic_df.set_index('key').join(issue_sum_df, on='key', rsuffix='_fact', how='inner')
    return sum_series


def get_dict_from_df(plan_df, fact_series, filter_list, plan_prefix, fact_prefix, with_total):
    plan_dict = dict()
    fact_dict = dict()

    for row in plan_df.itertuples():
        # issue can have several nums (features) in labels field
        feature_list = list_from_string(source_str=row.labels, reg_filter_list=filter_list, del_substring='num')

        f_name = row.description
        fg_name = row.summary

        count_of_features = len(feature_list)
        if count_of_features == 0:
            continue

        # if component has several nums, we devide it by nums count
        plan_est = float(row.timeoriginalestimate / count_of_features)

        if row.key in fact_series:
            fact_est = float(fact_series[row.key] / count_of_features)
        else:
            fact_est = 0.0

        total = 0.0

        # we should divide total estimate for every feature
        for num_item in feature_list:

            # feature = f_name
            plan_feature = plan_prefix + num_item.replace("_", " ")
            fact_feature = fact_prefix + num_item.replace("_", " ")

            # Tech writers have different issue type and use BOX as a component

            row_components = row.components

            if row_components is None or row_components == "":
                logging.warning('component is None: %s for %s', row.key, num_item)
                row_components = 'None [' + row.project + ']'

            row_component_list = row_components.split(',')

            plan_est = float(plan_est / len(row_component_list))
            fact_est = float(fact_est / len(row_component_list))

            for row_component in row_component_list:

                if row_component == 'BOX':
                    row_component = 'Documentation'

                if plan_feature in plan_dict:
                    if row_component in plan_dict[plan_feature]:
                        new_plan_est = plan_dict[plan_feature][row_component] + plan_est
                        new_fact_est = fact_dict[fact_feature][row_component] + fact_est

                        plan_dict[plan_feature][row_component] = new_plan_est
                        fact_dict[fact_feature][row_component] = new_fact_est
                    else:
                        plan_dict[plan_feature][row_component] = plan_est
                        fact_dict[fact_feature][row_component] = fact_est
                else:
                    plan_dict[plan_feature] = {row_component: plan_est}
                    fact_dict[fact_feature] = {row_component: fact_est}

                if with_total:
                    if TOTAL_NAME in plan_dict[plan_feature]:
                        plan_dict[plan_feature][TOTAL_NAME] = plan_dict[plan_feature][TOTAL_NAME] + \
                                                              plan_dict[plan_feature][
                                                                  row_components]
                        fact_dict[fact_feature][TOTAL_NAME] = fact_dict[fact_feature][TOTAL_NAME] + \
                                                              fact_dict[fact_feature][
                                                                  row_components]
                    else:
                        plan_dict[plan_feature][TOTAL_NAME] = plan_dict[plan_feature][row_components]
                        fact_dict[fact_feature][TOTAL_NAME] = fact_dict[fact_feature][row_components]

    return plan_dict, fact_dict


def prepare(epic_data, issue_data, or_filter_list, and_filter_list, plan_prefix, fact_prefix, with_total):
    # filter on Epic&Doc only

    # applying "OR" filter (features, feature group etc.)
    filtered_epic_df = applying_OR_filter(issue_df=epic_data, or_filter_list=or_filter_list)

    # applying "AND" filter
    filtered_epic_df = applying_AND_filter(issue_df=filtered_epic_df, and_filter_list=and_filter_list)

    # here should be fact calculation
    fact_series = get_fact_data(epic_df=epic_data, issue_df=issue_data)

    plan_dict, fact_dict = get_dict_from_df(plan_df=filtered_epic_df, fact_series=fact_series,
                                            filter_list=or_filter_list,
                                            plan_prefix=plan_prefix,
                                            fact_prefix=fact_prefix,
                                            with_total=with_total)

    plan_epic_df = pd.DataFrame.from_dict(plan_dict)
    fact_epic_df = pd.DataFrame.from_dict(fact_dict)
    return plan_epic_df, fact_epic_df
