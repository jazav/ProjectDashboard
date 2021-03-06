WITH epics AS (
SELECT e_ji.ID AS 'ID', CONCAT_WS('-', e_prj.pkey, e_ji.issuenum) AS 'Key', e_ji.SUMMARY AS 'Summary', e_it.pname AS 'Issue type', NULL AS 'Epic key', NULL AS 'Epic name',
		(CASE WHEN e_ji.TIMEORIGINALESTIMATE IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, e_ji.TIMEORIGINALESTIMATE))/28800) AS numeric(17,3)) END) AS 'Original estimate', NULL AS 'Spent time', 1 AS 'In sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS e_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS e_prj ON e_prj.ID = e_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS e_it ON e_it.ID = e_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[nodeassociation] AS e_na ON e_na.SOURCE_NODE_ID = e_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[projectversion] AS e_prjv ON e_prjv.ID = e_na.SINK_NODE_ID
	WHERE e_na.ASSOCIATION_TYPE = 'IssueFixVersion' AND e_it.pname = 'Epic'
		AND ((e_prj.pkey = 'IOTCMP' AND e_prjv.vname collate SQL_Latin1_General_CP1_CS_AS = '2.4.0' OR e_ji.SUMMARY LIKE 'SS10%')
		OR (e_prj.pkey = 'IOTAEP' AND (e_prjv.vname collate SQL_Latin1_General_CP1_CS_AS = '1.8.0' OR e_ji.SUMMARY LIKE 'SS10%')))),
t_spents AS (
	SELECT ji.ID AS 'ID', CONCAT_WS('-', prj.pkey, ji.issuenum) AS 'Key', ji.SUMMARY AS 'Summary', it.pname AS 'Issue type', e_link.[Epic key] AS 'Epic key', e_link.[Epic name] AS 'Epic name',
		MAX((CASE WHEN ji.TIMEORIGINALESTIMATE IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, ji.TIMEORIGINALESTIMATE))/28800) AS numeric(17,3)) END)) AS 'Original estimate',
		SUM(CAST((CONVERT(decimal, CONVERT(nvarchar, cgi.NEWVALUE))/28800) AS numeric(17,3)) - (CASE WHEN cgi.OLDVALUE IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, cgi.OLDVALUE))/28800) AS numeric(17,3)) END)) AS 'Spent time',
		(CASE WHEN e_link.[Epic key] IN (SELECT [Key] FROM epics) THEN 1 ELSE 0 END) AS 'In sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj ON prj.ID = ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS it ON it.ID = ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[changegroup] AS cg ON cg.issueid = ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[changeitem] AS cgi ON cgi.groupid = cg.ID
		LEFT JOIN (
			SELECT e_il.DESTINATION AS 'Destination', CONCAT_WS('-', e_prj.pkey, e_ji.issuenum) AS 'Epic key', e_ji.SUMMARY AS 'Epic name'
			FROM [srv-jira-prod-report].[dbo].[issuelink] AS e_il
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS e_ilt ON e_ilt.ID = e_il.LINKTYPE
				INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS e_ji ON e_ji.ID = e_il.SOURCE
				INNER JOIN [srv-jira-prod-report].[dbo].[project] AS e_prj ON e_prj.ID = e_ji.PROJECT
			WHERE e_ilt.LINKNAME = 'Epic-Story Link') AS e_link ON e_link.Destination = ji.ID
	WHERE cgi.FIELD = 'timespent' AND (cg.CREATED BETWEEN '2019-05-01 00:00:00.000' AND GETDATE()) AND prj.pkey in ('IOTCMP', 'IOTAEP') AND it.pname NOT IN ('Epic', 'Sub-task')
	GROUP BY ji.ID, CONCAT_WS('-',prj.pkey, ji.issuenum), ji.SUMMARY, it.pname, e_link.[Epic key], e_link.[Epic name]),
st_spents AS (
	SELECT ji.ID AS 'ID', CONCAT_WS('-',prj.pkey, ji.issuenum) AS 'Key', ji.SUMMARY AS 'Summary', it.pname AS 'Issue type', t_link.[Epic key] AS 'Epic key', t_link.[Epic name] AS 'Epic name',
		MAX((CASE WHEN ji.TIMEORIGINALESTIMATE IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, ji.TIMEORIGINALESTIMATE))/28800) AS numeric(17,3)) END)) AS 'Original estimate',
		SUM(CAST((CONVERT(decimal, CONVERT(nvarchar, cgi.NEWVALUE))/28800) AS numeric(17,3)) - (CASE WHEN cgi.OLDVALUE IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, cgi.OLDVALUE))/28800) AS numeric(17,3)) END)) AS 'Spent time',
		(CASE WHEN t_link.[Epic key] IN (SELECT [Key] FROM epics) THEN 1 ELSE 0 END) AS 'In sprint'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj ON prj.ID = ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS it ON it.ID = ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[changegroup] AS cg ON cg.issueid = ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[changeitem] AS cgi ON cgi.groupid = cg.ID
		INNER JOIN (
			SELECT t_il.DESTINATION AS 'Destination', e_link.[Epic key] AS 'Epic key', e_link.[Epic name] AS 'Epic name'
			FROM [srv-jira-prod-report].[dbo].[issuelink] AS t_il
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS t_ilt ON t_ilt.ID = t_il.LINKTYPE
				INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS t_ji ON t_ji.ID = t_il.SOURCE
				LEFT JOIN (
					SELECT e_il.DESTINATION AS 'Destination', CONCAT_WS('-', e_prj.pkey, e_ji.issuenum) AS 'Epic key', e_ji.SUMMARY AS 'Epic name'
					FROM [srv-jira-prod-report].[dbo].[issuelink] AS e_il
						INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS e_ilt ON e_ilt.ID = e_il.LINKTYPE
						INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS e_ji ON e_ji.ID = e_il.SOURCE
						INNER JOIN [srv-jira-prod-report].[dbo].[project] AS e_prj ON e_prj.ID = e_ji.PROJECT
					WHERE e_ilt.LINKNAME = 'Epic-Story Link') AS e_link ON e_link.Destination = t_ji.ID
			WHERE t_ilt.LINKNAME = 'jira_subtask_link') AS t_link ON t_link.Destination = ji.ID
	WHERE cgi.FIELD = 'timespent' AND (cg.CREATED BETWEEN '2019-05-01 00:00:00.000' AND GETDATE()) AND prj.pkey in ('IOTCMP', 'IOTAEP') AND it.pname = 'Sub-task'
	GROUP BY ji.ID, CONCAT_WS('-',prj.pkey, ji.issuenum), ji.SUMMARY, it.pname, t_link.[Epic key], t_link.[Epic name])

SELECT ji.ID AS 'ID', CONCAT_WS('-', prj.pkey, ji.issuenum) AS 'Key', ji.SUMMARY AS 'Summary', it.pname AS 'Issue type', NULL AS 'Epic key', NULL AS 'Epic name',
	(CASE WHEN ji.TIMEORIGINALESTIMATE IS NULL THEN 0 ELSE CAST((CONVERT(decimal, CONVERT(nvarchar, ji.TIMEORIGINALESTIMATE))/28800) AS numeric(17,3)) END) AS 'Original estimate', NULL AS 'Spent time',
	(CASE WHEN CONCAT_WS('-', prj.pkey, ji.issuenum) IN (SELECT [Key] FROM epics) THEN 1 ELSE 0 END) AS 'In sprint'
FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji
	INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj ON prj.ID = ji.PROJECT
	INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS it ON it.ID = ji.issuetype
WHERE ((CONCAT_WS('-', prj.pkey, ji.issuenum) IN (SELECT [Epic key] FROM t_spents UNION ALL SELECT [Epic key] FROM st_spents)))
UNION ALL
SELECT * FROM t_spents
UNION ALL
SELECT * FROM st_spents
UNION
SELECT * FROM epics
ORDER BY [Issue type], [Key]