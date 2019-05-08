set lines 200
set echo off
set verify off
col username for a10
col sess for a35 heading 'sid:serial:os session'
col instance_name for a8
col sql_id for a20
col lo_type for a25 heading 'TYPE'
col lock_object for a40
col sqlid for a20 heading 'SQL_ID|SQL_CHILD_NUMBER'
set pages 200
set heading on
col q_l   for a20 heading 'LMODE:QUEST'
col status for a10
col event for a20
col id for a20 heading 'ID1:ID2'

--SELECT b.username,
--            DECODE (a.request, 0, 'Holder: ', 'Waiter: ')
--         || c.instance_name
--         || ':'
--         || a.sid||':'||b.serial#||':'||d.spid 
--            sess,b.status,
--            DECODE (b.sql_id, '', b.prev_sql_id, b.sql_id)
--         || ':'
--         || sql_child_number
--            AS SQLID ,
--         a.id1||':'||
--         a.id2 id,
--         DECODE (a.lmode,
--                 1, '1||No Lock',
--                 2, '2||Row Share',
--                 3, '3||Row Exclusive',
--                 4, '4||Share',
--                 5, '5||Shr Row Excl',
--                 6, '6||Exclusive',
--                 'NULL')||':'||
--        DECODE (a.REQUEST,
--                 1, '1||No Lock',
--                 2, '2||Row Share',
--                 3, '3||Row Exclusive',
--                 4, '4||Share',
--                 5, '5||Shr Row Excl',
--                 6, '6||Exclusive',
--                 'NULL') q_l,
--         DECODE (a.TYPE,
--                 'CF', 'CF|Control File',
--                 'DX', 'DX|Distrted Transaction',
--                 'FS', 'FS|File Set',
--                 'IR', 'IR|Instance Recovery',
--                 'IS', 'IS|Instance State',
--                 'IV', 'Libcache Invalidation',
--                 'LS', 'LogStartORswitch',
--                 'MR', 'MR|Media Recovery',
--                 'RT', 'RT|Redo Thread',
--                 'RW', 'RW|Row Wait',
--                 'SQ', 'SQ|Sequence #',
--                 'ST', 'Diskspace Transaction',
--                 'TE', 'TE|Extend Table',
--                 'TT', 'TT|Temp Table',
--                 'TX', 'TX|Transaction enqueue',
--                 'TM', 'TM|Dml enqueue',
--                 'UL', 'UL|PLSQL User_lock',
--                 'UN', 'UN|User Name',
--                 'Other type')
--            lo_type,a.block,
--         a.ctime,
--         substr(b.event,1,20) event
--    FROM GV$LOCK a, gv$session b,gv$process d
--   WHERE     (a.id1, a.id2, a.TYPE) IN (SELECT id1, id2, TYPE
--                                          FROM GV$LOCK
--                                         WHERE request > 0)
--         AND b.inst_id = a.inst_id
--         AND a.sid = b.sid
--         AND b.inst_id =d.inst_id
--         AND b.paddr=d.addr
--ORDER BY id1, request
--/
SELECT b.username,
            DECODE (a.request, 0, 'Holder: ', 'Waiter: ')||a.inst_id
         || ':'
         || a.sid||':'||b.serial#||':'||d.spid 
            sess,b.status,
            DECODE (b.sql_id, '', b.prev_sql_id, b.sql_id)
         || ':'
         || sql_child_number
            AS SQLID ,
         a.id1||':'||
         a.id2 id,
         DECODE (a.lmode,
                 1, '1||No Lock',
                 2, '2||Row Share',
                 3, '3||Row Exclus',
                 4, '4||Share',
                 5, '5||Shr Row Excl',
                 6, '6||Exclusive',
                 'NULL')||':'||
        DECODE (a.REQUEST,
                 1, '1||No Lock',
                 2, '2||Row Share',
                 3, '3||Row Excl',
                 4, '4||Share',
                 5, '5||Shr Row Excl',
                 6, '6||Exclusive',
                 'NULL') q_l,
         DECODE (a.TYPE,
                 'CF', 'CF|Control File',
                 'DX', 'DX|Distrted Trans',
                 'FS', 'FS|File Set',
                 'IR', 'IR|Inst Recov',
                 'IS', 'IS|Instance State',
                 'IV', 'Libcache Invalid',
                 'LS', 'LogStartORswitch',
                 'MR', 'MR|Media Recovery',
                 'RT', 'RT|Redo Thread',
                 'RW', 'RW|Row Wait',
                 'SQ', 'SQ|Sequence #',
                 'ST', 'Diskspace Trans',
                 'TE', 'TE|Extend Table',
                 'TT', 'TT|Temp Table',
                 'TX', 'TX|Transaction enqueue',
                 'TM', 'TM|Dml enqueue',
                 'UL', 'UL|PLSQL User_lock',
                 'UN', 'UN|User Name',
                 'Other type')
            lo_type,a.block,
         a.ctime,
         substr(b.event,1,20) event
    FROM GV$LOCK a, gv$session b,gv$process d
   WHERE     (a.id1, a.id2, a.TYPE) IN (SELECT id1, id2, TYPE
                                          FROM GV$LOCK
                                         WHERE request > 0)
         AND b.inst_id = a.inst_id
         AND a.sid = b.sid
         AND b.inst_id =d.inst_id
         AND b.paddr=d.addr
ORDER BY id1, request
/





--SELECT 'sessiion ' || sid || ' wait object name : ' || object_name as "lock_object"
--  FROM (SELECT DISTINCT a.sid, c.object_name
--          FROM GV$LOCK a, gv$locked_object b, dba_objects c
--         WHERE     (a.id1, a.id2, a.TYPE) IN (SELECT id1, id2, TYPE
--                                                FROM GV$LOCK
--                                               WHERE request > 0)
--               AND a.sid = b.session_id
--               AND b.object_id = c.object_id
--               AND a.request > 0);*/
--
