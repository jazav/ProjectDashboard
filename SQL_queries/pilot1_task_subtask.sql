WITH user_stories AS (
	SELECT us_ji.ID AS 'id', CONCAT_WS('-', us_prj.pkey, us_ji.issuenum) AS 'key', us_it.pname AS 'issue type', us_is.pname AS 'status', NULL AS 'resolution date',
		NULL AS 'component', NULL AS 'L3', (CASE WHEN bulks.Estimate IS NULL THEN '' ELSE CONCAT('"', bulks.Component, '": "', bulks.Estimate, '"') END) AS 'estimate',
		(CASE WHEN us_pp.ID IS NOT NULL THEN 'Pilot 1.0' ELSE NULL END) AS 'Pilot 1.0', (CASE WHEN us_core.ID IS NOT NULL THEN 'Core' ELSE NULL END) AS 'Core',
		(CASE WHEN us_custom.ID IS NOT NULL THEN 'Custom' ELSE NULL END) AS 'Custom', (CASE WHEN us_config.ID IS NOT NULL THEN 'Config' ELSE NULL END) AS 'Config'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS us_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS us_it ON us_it.ID = us_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS us_prj ON us_prj.ID = us_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS us_is ON us_is.ID = us_ji.issuestatus
		LEFT JOIN [srv-jira-prod-report].[dbo].[label] AS us_lbl ON us_lbl.ISSUE = us_ji.ID
		LEFT JOIN (
			SELECT be.ISSUE_ID, be.[VALUE] AS 'Estimate', cmp.cname AS 'Component'
			FROM [srv-jira-prod-report].[dbo].[AO_983835_BE_ITEM] AS be
				INNER JOIN [srv-jira-prod-report].[dbo].[component] AS cmp ON cmp.ID = be.COMPONENT_ID) AS bulks ON bulks.ISSUE_ID = us_ji.ID
		LEFT JOIN (SELECT pp_ji.ID FROM [srv-jira-prod-report].[dbo].[label] AS pp_lbl
			INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS pp_ji ON pp_ji.ID = pp_lbl.ISSUE WHERE pp_lbl.LABEL = 'PilotPriority') AS us_pp ON us_pp.ID = us_ji.ID
		LEFT JOIN (SELECT core_ji.ID FROM [srv-jira-prod-report].[dbo].[label] AS core_lbl
			INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS core_ji ON core_ji.ID = core_lbl.ISSUE WHERE core_lbl.LABEL = 'Core') AS us_core ON us_core.ID = us_ji.ID
		LEFT JOIN (SELECT custom_ji.ID FROM [srv-jira-prod-report].[dbo].[label] AS custom_lbl
			INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS custom_ji ON custom_ji.ID = custom_lbl.ISSUE WHERE custom_lbl.LABEL = 'Custom') AS us_custom ON us_custom.ID = us_ji.ID
		LEFT JOIN (SELECT config_ji.ID FROM [srv-jira-prod-report].[dbo].[label] AS config_lbl
			INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS config_ji ON config_ji.ID = config_lbl.ISSUE WHERE config_lbl.LABEL = 'Config') AS us_config ON us_config.ID = us_ji.ID
	WHERE us_prj.pname = 'BSSBOX' AND us_it.pname = 'User Story (L3)' AND us_is.pname != 'Canceled' AND us_lbl.LABEL = 'PilotPriority'),
epics AS (
	SELECT DISTINCT e_ji.ID AS 'id', CONCAT_WS('-', e_prj.pkey, e_ji.issuenum) AS 'key', e_it.pname AS 'issue type', e_is.pname AS 'status', CONVERT(date, e_ji.RESOLUTIONDATE) AS 'resolution date',
		epics_cmp.Component AS 'component', user_stories.[key] AS 'L3', NULL AS 'estimate', user_stories.[Pilot 1.0] AS 'Pilot 1.0', user_stories.Core AS 'Core', user_stories.[Custom] AS 'Custom', user_stories.Config AS 'Config'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS e_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS e_il ON e_il.DESTINATION = e_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS e_ilt ON e_ilt.ID = e_il.LINKTYPE
		INNER JOIN user_stories ON user_stories.ID = e_il.SOURCE
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS e_it ON e_it.ID = e_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS e_is ON e_is.ID = e_ji.issuestatus
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS e_prj ON e_prj.ID = e_ji.PROJECT
		LEFT JOIN (
			SELECT ec_ji.ID AS 'ID', ec_cmp.cname AS 'Component'
			FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ec_ji
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS ec_il ON ec_il.DESTINATION = ec_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS ec_ilt ON ec_ilt.ID = ec_il.LINKTYPE
				INNER JOIN [srv-jira-prod-report].[dbo].[nodeassociation] AS ec_na ON ec_na.SOURCE_NODE_ID = ec_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[component] AS ec_cmp ON ec_cmp.ID = ec_na.SINK_NODE_ID
			WHERE ec_ilt.LINKNAME = 'nexign_hierarchy_link' AND ec_il.SOURCE IN (SELECT ID FROM user_stories) AND ec_na.ASSOCIATION_TYPE = 'IssueComponent') AS epics_cmp ON epics_cmp.ID = e_ji.ID
	WHERE e_ilt.LINKNAME = 'nexign_hierarchy_link' AND e_il.SOURCE IN (SELECT ID FROM user_stories) AND e_is.pname != 'Canceled')

SELECT id, [key], [issue type], [status], [resolution date], component, L3, CONCAT('{', STRING_AGG(estimate, ', '), '}') AS 'estimate', [Pilot 1.0], Core, [Custom], Config
FROM user_stories
GROUP BY id, [key], [issue type], [status], [resolution date], component, L3, [Pilot 1.0], Core, [Custom], Config
UNION ALL
SELECT * FROM epics
ORDER  BY [Issue type] DESC, [Resolution date]