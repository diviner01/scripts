set echo off
set verify off
set heading on
set serveroutput on
set feedback off
set lines 300
set pages 10000
set long 100000
col i_mem for 999999 heading 'SHARED|Mem KB'
col sorts for 99999999
col version_count for 999 heading 'VER|NUM'
col loaded_versions for 999 heading 'Loaded|NUM'
col open_versions for 999 heading 'Open|NUM'
col executions for 999999999 heading 'EXEC|NUM'
col parse_calls for 999999999 heading 'PARSE|CALLS'
col disk_reads for 999999999 heading 'DISK|READ'
col direct_writes for 999999 heading 'DIRECT|WRITE'
col buffer_gets for 99999999999999
col avg_disk_read for 99999 heading 'AVG|DISK|READ'
col avg_direct_write for 99999 heading 'AVG|DIRECT|WRITE'
col avg_buffer_get for 9999999 heading 'AVG|BUFFER|GET'
col sql_profile for a34
col ROWS_PROCESSED for 999999999 heading 'ROW|PROC'
col avg_row_proc for 99999999 heading 'AVG|ROW|PROC'
undefine sqlid
select sql_fulltext from v$sqlarea where sql_id='&&sqlid';
set pages 40
SELECT round(sharable_mem / 1024, 2) i_mem,
       sorts,
       version_count,
       loaded_versions,
       OPEN_VERSIONS,
       executions,
       PARSE_CALLS,
       disk_reads,
       trunc(disk_reads / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_disk_read,
       direct_writes,
       trunc(direct_writes / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_direct_write,
       buffer_gets,
       trunc(buffer_gets / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_buffer_get,
       ROWS_PROCESSED,
       trunc(ROWS_PROCESSED / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_row_proc,
       sql_profile
  FROM v$sqlarea
 where sql_id = '&&sqlid'
/
col c_p for a16 heading 'CHILD_NUMBER|PLAN_HASH_VALUE'
col PARSING_SCHEMA_NAME for a15 heading 'USER_NAME'
col USERS_OPENING for 9999 heading 'USER|DOING'
col time for a15 heading 'AVG_TIME'
SELECT PARSING_SCHEMA_NAME,
       CHILD_NUMBER || ':' || plan_hash_value c_p,
       round(sharable_mem / 1024, 2) i_mem,
       sorts,
       USERS_OPENING,
       executions,
       PARSE_CALLS,
       disk_reads,
       trunc(disk_reads / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_disk_read,
--       direct_writes,
--       trunc(direct_writes / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_direct_write,
       buffer_gets,
       trunc(buffer_gets / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_buffer_get,
       ROWS_PROCESSED,
       trunc(ROWS_PROCESSED / decode(EXECUTIONS, 0, 1, EXECUTIONS)) avg_row_proc,
       trunc(CPU_TIME / decode(EXECUTIONS, 0, 1, EXECUTIONS)) || ':' ||
       trunc(ELAPSED_TIME / decode(EXECUTIONS, 0, 1, EXECUTIONS)) time,
       sql_profile
  FROM v$sql
 where sql_id = '&&sqlid'
/
undefine sqlid