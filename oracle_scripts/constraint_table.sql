-- File Name : 
-- Description : 
-- DB Verson：10g、11g、12c
-- Date : 2015/09/05
-- Author ：黄廷忠 tingzhong.huang
-- QQ:7343696
-- http://www.htz.pw
-- 
-- Histroy:


col name	format a22 heading 'Name'
set echo off
set heading on
set lines 300
set verify off
col name for a20 heading 'Constraint|Name'
col type	format a20  heading 'Type'
col stat	format a10  heading 'status'
col ref_tab	format a20 heading 'Reference|Object' 
col ref_con	format a22 heading 'Reference|Constraint'
col index_name for a20 heading 'Index |Name'
col column_name for a15 heading 'Column|Name'
col owner_name for a25 heading 'Owner|tablename'
set pages 10000
col owner for a15 
undefine owner;
undefine tablename;
 
 SELECT distinct a.owner || ':' || a.table_name owner_name,
       a.constraint_name name,
       c.column_name,
       DECODE(a.constraint_type,
              'C',
              'Check or Not null',
              'R',
              'Foreign Key',
              'P',
              'Primary key',
              'U',
              'Unique',
              '*') TYPE,
       a.status,
       b.owner || '.' || b.table_name ref_tab,
       a.r_constraint_name ref_con,
       a.index_name
  FROM dba_constraints a, dba_constraints b, dba_cons_columns c
 WHERE a.owner = nvl(UPPER('&&owner'), a.owner)
   AND a.table_name = nvl(UPPER('&&tablename'), a.table_name)
   AND a.r_constraint_name = b.constraint_name(+)
   AND a.constraint_name = c.constraint_name
union all
SELECT distinct a.owner || ':' || a.table_name owner_name,
       a.constraint_name name,
       c.column_name,
       DECODE(a.constraint_type,
              'C',
              'Check or Not null',
              'R',
              'Foreign Key',
              'P',
              'Primary key',
              'U',
              'Unique',
              '*') TYPE,
       a.status,
       b.owner || '.' || b.table_name ref_tab,
       a.r_constraint_name ref_con,
       a.index_name
  FROM dba_constraints a, dba_constraints b, dba_cons_columns c
 WHERE b.owner = nvl(UPPER('&&owner'), b.owner)
   AND b.table_name = nvl(UPPER('&&tablename'), b.table_name)
   AND a.r_constraint_name = b.constraint_name(+)
   AND a.constraint_name = c.constraint_name
 ORDER BY 1
/
undefine owner
undefine tablename
