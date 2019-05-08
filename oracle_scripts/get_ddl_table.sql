-- File Name : get_ddl_table.sql
-- Purpose : 显示表、表的注释、表的索引、约束、对象权限的DDL.
-- Date : 2015/09/05
-- 认真就输、QQ:7343696
-- http://www.htz.pw
set echo off
SET LONG 20000 LONGCHUNKSIZE 20000 PAGESIZE 0 LINESIZE 1000 FEEDBACK OFF VERIFY OFF TRIMSPOOL ON
col getddl for a2000
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'SQLTERMINATOR', true);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'STORAGE',false);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'SEGMENT_ATTRIBUTES',false);
EXECUTE DBMS_METADATA.SET_TRANSFORM_PARAM(DBMS_METADATA.SESSION_TRANSFORM,'TABLESPACE',false);
--用于生成间隔分区表的，默认间隔分区表不生成自动创建的分区
exec dbms_metadata.set_transform_param(dbms_metadata.SESSION_TRANSFORM,'EXPORT',true);


ACCEPT TABLE_OWNER CHAR PROMPT 'Enter Table Owner : '
ACCEPT TABLE_NAME CHAR PROMPT 'Enter Table Name : '


/* Formatted on 2015/09/05 16:50:41 (QP5 v5.240.12305.39446) */
SELECT DBMS_METADATA.GET_DDL ('TABLE', OBJECT_NAME, OWNER)
  FROM Dba_objects
 WHERE     owner = UPPER ('&TABLE_OWNER')
       AND object_name = UPPER ('&TABLE_NAME')
       AND object_type = 'TABLE'
UNION ALL
SELECT DBMS_METADATA.GET_DEPENDENT_DDL ('COMMENT', TABLE_NAME, OWNER)
  FROM (SELECT table_name, owner
          FROM Dba_col_comments
         WHERE     owner = UPPER ('&TABLE_OWNER')
               AND table_name = UPPER ('&TABLE_NAME')
               AND comments IS NOT NULL
        UNION
        SELECT table_name, owner
          FROM sys.Dba_TAB_comments
         WHERE     owner = UPPER ('&TABLE_OWNER')
               AND table_name = UPPER ('&TABLE_NAME')
               AND comments IS NOT NULL)
UNION ALL
SELECT DBMS_METADATA.GET_DEPENDENT_DDL ('INDEX', TABLE_NAME, TABLE_OWNER)
  FROM (SELECT table_name, table_owner
          FROM Dba_indexes
         WHERE     table_owner = UPPER ('&TABLE_OWNER')
               AND table_name = UPPER ('&TABLE_NAME')
               AND index_name NOT IN
                      (SELECT constraint_name
                         FROM sys.Dba_constraints
                        WHERE     table_name = table_name
                              AND constraint_type = 'P')
               AND ROWNUM = 1)
UNION ALL
SELECT DBMS_METADATA.GET_DDL ('TRIGGER', trigger_name, owner)
  FROM Dba_triggers
 WHERE     table_owner = UPPER ('&TABLE_OWNER')
       AND table_name = UPPER ('&TABLE_NAME')
UNION ALL
SELECT DBMS_METADATA.GET_DEPENDENT_DDL ('REF_CONSTRAINT', table_name, OWNER)
  FROM dba_constraints
 WHERE     owner = UPPER ('&TABLE_OWNER')
       AND table_name = UPPER ('&TABLE_NAME')
       AND CONSTRAINT_TYPE = 'R'
       AND ROWNUM = 1
UNION ALL
SELECT DBMS_METADATA.GET_DEPENDENT_DDL ('CONSTRAINT', TABLE_NAME, OWNER)
  FROM dba_constraints
 WHERE     owner = UPPER ('&TABLE_OWNER')
       AND table_name = UPPER ('&TABLE_NAME')
       AND CONSTRAINT_TYPE <> 'R'
       AND ROWNUM = 1
UNION ALL
SELECT DBMS_METADATA.get_dependent_ddl ('OBJECT_GRANT', TABLE_NAME, OWNER)
  FROM dba_tab_privs
 WHERE     owner = UPPER ('&TABLE_OWNER')
       AND table_name = UPPER ('&TABLE_NAME')
       AND ROWNUM = 1
UNION ALL
SELECT DBMS_METADATA.get_ddl ('SYNONYM', synonym_name, owner)
  FROM dba_synonyms 
 WHERE     table_owner = UPPER ('&TABLE_OWNER')
       AND table_name = UPPER ('&TABLE_NAME')
/
undefine TABLE_OWNER;
undefine TABLE_NAME;
