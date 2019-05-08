set lines 130 pages 1000
col stat_name for a25
col BEGIN_INTERVAL_TIME for a25
col END_INTERVAL_TIME for a25
col redo_size for '999,999,990.99'
col sess_l_reads for '999,999,990.99'
col blk_change for '999,999,990.99'
col phy_reads for '999,999,990.99'
col phy_writes for '999,999,990.99'
col user_calls for '999,999,990.99'
col parse_count_tot for '999,999,990.99'
col parse_count_hard for '999,999,990.99'
col sort_disk for '999,999,990.99'
col logons for '999,999,990.99'
col execute_count for '999,999,990.99'
col trans for '999,999,990.99'
select
date_time,
sum(case   WHEN stat_name='redo size' then round((e_val - b_val)/sec,2) else null end)              redo_size,
sum(case   WHEN stat_name='session logical reads' then round((e_val - b_val)/sec,2) else null end)  sess_l_reads,
sum(case   WHEN stat_name='db block changes' then round((e_val - b_val)/sec,2) else null end)       blk_change,
sum(case   WHEN stat_name='physical reads' then round((e_val - b_val)/sec,2) else null end)         phy_reads,
sum(case   WHEN stat_name='physical writes' then round((e_val - b_val)/sec,2) else null end)        phy_writes,
sum(case   WHEN stat_name='user calls' then round((e_val - b_val)/sec,2) else null end)             user_calls,
--sum(case WHEN stat_name='parse count (total)' then round((e_val - b_val)/sec,2) else null end)    parse_count_tot,
--sum(case WHEN stat_name='parse count (hard)' then round((e_val - b_val)/sec,2) else null end)     parse_count_hard,
--sum(case WHEN stat_name='sorts (disk)' then round((e_val - b_val)/sec,2) else null end)           sort_disk,
sum(case   WHEN stat_name='logons cumulative' then round((e_val - b_val)/sec,2) else null end)      logons,
sum(case   WHEN stat_name='execute count' then round((e_val - b_val)/sec,2) else null end)          execute_count,
round((sum(case WHEN stat_name='user commits' then (e_val - b_val)/sec else null end) +
sum(case WHEN stat_name='user rollbacks' then (e_val - b_val)/sec else null end)),2) trans
from
(
select
to_char(sn.BEGIN_INTERVAL_TIME,'mm/dd/yy_hh24_mi')|| to_char(sn.END_INTERVAL_TIME,'_hh24_mi') Date_Time,
b.stat_name stat_name,
e.value e_val,
b.value b_val,
(extract( day from (end_interval_time-begin_interval_time) )*24*60*60+
extract( hour from (end_interval_time-begin_interval_time) )*60*60+
extract( minute from (end_interval_time-begin_interval_time) )*60+
extract( second from (end_interval_time-begin_interval_time)) ) sec
FROM
dba_hist_sysstat b,
dba_hist_sysstat e,
dba_hist_snapshot sn
where
begin_interval_time > trunc((sysdate - &before_hours/24),'HH24') and
b.snap_id(+) = e.snap_id-1
and e.snap_id = sn.snap_id
and b.dbid(+) = e.dbid
and e.dbid = (select dbid from v$database)
and sn.dbid = (select dbid from v$database)
and b.instance_number(+) = e.instance_number
and e.instance_number = (select instance_number from v$instance)
and sn.instance_number = (select instance_number from v$instance)
and b.instance_number(+) = e.instance_number
and b.stat_name = e.stat_name
and b.stat_name in (
'redo size',
'session logical reads',
'db block changes',
'physical reads',
'physical writes',
'user calls',
'parse count (total)',
'parse count (hard)',
'sorts (disk)',
'logons cumulative',
'execute count',
'transactions',
'user commits',
'user rollbacks'
)
)
group by date_time
Order by date_time
;