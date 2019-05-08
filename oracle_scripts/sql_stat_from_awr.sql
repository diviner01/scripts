set echo off
set lines 300
set verify off
set serveroutput on
set feedback off
set lines 300
set pages 10000
set long 100000
@awr_snapshot_info.sql
set lines 300
set echo off
set verify off
col sql_id for a18
col i_mem for 999999 heading 'SHARED|Mem KB'
col sorts for 99999999
col version_count for 999 heading 'VER|NUM'
col executions for 999999 heading 'EXEC|NUM'
col parse_calls for 999999 heading 'PARSE|CALLS'
col disk_reads for 999999 heading 'DISK|READ'
col direct_writes for 999999 heading 'DIRECT|WRITE'
col buffer_gets for 99999999999999
col avg_disk_reads for 99999 heading 'AVG|DISK|READ'
col avg_direct_writes for 99999 heading 'AVG|DIRECT|WRITE'
col avg_buffer_gets for 9999999 heading 'AVG|BUFFER|GET'
col sql_profile for a14
col ROWS_PROCESSED for 999999999 heading 'ROW|PROC'
col avg_rows_processed for 99999999 heading 'AVG|ROW|PROC'
col  avg_fetches for 999999 heading 'AVG|FETCH'
col AVG_ELAPSED_TIME  for 9999999 heading 'AVG|ELAPSED|TIME'
col AVG_CPU_TIME for 9999999 heading 'AVG|CPU_TIME'
col PARSING_SCHEMA_NAME  for a15 heading 'PARSING|SCHEMA_NAME'
SELECT 
       plan_hash_value,
       parsing_schema_name,
       (executions) executions,
       (elapsed_time) elapsed_time,
       TRUNC ( (elapsed_time) / DECODE ( (executions), 0, 1, (executions)))
          avg_elapsed_time,
       (cpu_time) cpu_time,
       TRUNC ( (cpu_time) / DECODE ( (executions), 0, 1, (executions)))
          avg_cpu_time,
       (buffer_gets) buffer_gets,
       TRUNC ( (buffer_gets) / DECODE ( (executions), 0, 1, (executions)))
          avg_buffer_gets,
       (disk_reads) disk_reads,
       TRUNC ( (disk_reads) / DECODE ( (executions), 0, 1, (executions)))
          avg_disk_reads,
       (direct_writes) direct_writes,
       TRUNC ( (direct_writes) / DECODE ( (executions), 0, 1, (executions)))
          avg_direct_writes,
       (rows_processed) rows_processed,
       TRUNC ( (rows_processed) / DECODE ( (executions), 0, 1, (executions)))
          avg_rows_processed,
       (fetches) fetches,
       TRUNC ( (fetches) / DECODE ( (executions), 0, 1, (executions)))
          avg_fetches
  FROM TABLE (
          DBMS_SQLTUNE.select_workload_repository (&begin_id,
                                                 &end_id,
                                                   'sql_id=''&sqlid'''));
undefine begin_id;
undefine sqlid;
undefine end_id;
undefine sort_type;
undefine topn;

