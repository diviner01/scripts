set echo off
set heading on
set lines 200
set verify off
set pagesize 999
col username format a13
col prog format a22
col sqltext format a190
col sid format 999
col child_number format 99999 heading CHILD
col ocategory format a10
col avg_etime format 9,999,999.99
col etime format 9,999,999.99

SELECT sql_id,
       child_number,
       hash_value,
       plan_hash_value plan_hash,
       executions execs,
       elapsed_time / 1000000 etime,
         (elapsed_time / 1000000)
       / DECODE (NVL (executions, 0), 0, 1, executions)
          avg_etime,
       u.username,
       sql_text sqltext
  FROM v$sql s, dba_users u
 WHERE     sql_text  LIKE '%&sql_text%'
       AND sql_text NOT LIKE '%from v$sql where sql_text like nvl(%'
       AND sql_id LIKE NVL ('&sql_id', sql_id)
       AND u.user_id = s.parsing_user_id
/
