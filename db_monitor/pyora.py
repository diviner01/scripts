#!/usr/bin/env python
# coding: utf-8
# vim: tabstop=2 noexpandtab
"""
    Author: Danilo F. Chilene
	Email:	bicofino at gmail dot com
"""

import argparse
import cx_Oracle
import inspect
import json
import re
import sys
import urllib,urllib2
import os

version = 0.2

#   保证发送的不乱码
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


class Checks(object):


    def check_sequenceused(self):
        """Check sequence used"""
        sql = "SELECT ROUND(MAX(LAST_NUMBER / MAX_VALUE),3) as businessData \
               FROM DBA_SEQUENCES T \
               WHERE T.CYCLE_FLAG = 'N'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def check_passwd_expire(self,exp_date):
        """Check passwoed expire"""
        sql = """select 'UserNames:'||listagg(username,',') WITHIN GROUP (ORDER BY username)||' expire after '||round(expiry_date - sysdate)||' days' as text
            from dba_users 
            where expiry_date is not null 
              and (expiry_date - sysdate)<={0}
              and username not in ('SYS','SCOTT',
'GOLDENGATE',
'OUTLN',
'MGMT_VIEW',
'FLOWS_FILES',
'MDSYS',
'ORDSYS',
'EXFSYS',
'DBSNMP',
'WMSYS',
'APPQOSSYS',
'APEX_030200',
'OWBSYS_AUDIT',
'ORDDATA',
'CTXSYS',
'ANONYMOUS',
'SYSMAN',
'XDB',
'ORDPLUGINS',
'OWBSYS',
'SI_INFORMTN_SCHEMA',
'OLAPSYS',
'ORACLE_OCM',
'XS$NULL',
'BI',
'PM',
'MDDATA',
'IX',
'SH',
'DIP',
'OE',
'APEX_PUBLIC_USER',
'HR',
'SPATIAL_CSW_ADMIN_USR',
'SPATIAL_WFS_ADMIN_USR',
'AUDSYS',
'DMSYS',
'DVF',
'DVSYS',
'EXDSYS',
'GSMADMIN_INTERNAL',
'GSMCATUSER',
'GSMUSER',
'LBACSYS',
'MTSSYS',
'ODM',
'ODM_MTR',
'OJVMSYS',
'SYSBACKUP',
'SYSDG',
'SYSKM',
'TSMSYS',
'WKPROXY',
'WKSYS',
'WK_TEST',
'XTISYS',
'AURORA$JIS$UTILITY$',
'AURORA$ORB$UNAUTHENTICATED',
'DSSYS',
'OSE$HTTP$ADMIN',
'PERFSTAT') 
group by  round(expiry_date - sysdate) """.format(exp_date)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        count = self.cur.rowcount
        if count==0:
           print 'none'
        for i in res:
            print i[0] 
    def check_file_autoextend(self):
        """Check file autoextend"""
        sql = "select count(1) \
            from dba_data_files \
            where autoextensible = 'YES' \
            and tablespace_name not in ('SYSTEM', 'SYSAUX')"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def check_tabind_degree(self):
        """check_tabind_degree"""
        sql = "select j.a + k.b + m.c + n.d \
             from (select count(0) a \
             from dba_tables \
             where degree > 1 \
             and degree not like '%DEFAULT%' \
             and TABLE_NAME not like '%$%') j, \
             (select count(0) b \
             from dba_indexes \
             where degree > 1 \
             and degree not like '%DEFAULT%' \
             and index_NAME not like '%$%') k, \
             (select count(0) c \
             from dba_tables \
             where degree = 'DEFAULT' \
             and TABLE_NAME not like '%$%') m, \
             (select count(0) d \
             from dba_indexes \
             where degree = 'DEFAULT' \
             and index_NAME not like '%$%') n"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def check_active(self):
        """Check Intance is active and open"""
        sql = "select to_char(case when inst_cnt > 0 then 1 else 0 end, \
              'FM99999999999999990') retvalue from (select count(*) inst_cnt \
              from v$instance where status = 'OPEN' and logins = 'ALLOWED' \
              and database_status = 'ACTIVE')"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def rcachehit(self):
        """Read Cache hit ratio"""
        sql = "SELECT to_char((1 - (phy.value - lob.value - dir.value) / \
              ses.value) * 100, 'FM99999990.9999') retvalue \
              FROM   v$sysstat ses, v$sysstat lob, \
              v$sysstat dir, v$sysstat phy \
              WHERE  ses.name = 'session logical reads' \
              AND    dir.name = 'physical reads direct' \
              AND    lob.name = 'physical reads direct (lob)' \
              AND    phy.name = 'physical reads'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dsksortratio(self):
        """Disk sorts ratio"""
        sql = "SELECT to_char(d.value/(d.value + m.value)*100, \
              'FM99999990.9999') retvalue \
              FROM  v$sysstat m, v$sysstat d \
              WHERE m.name = 'sorts (memory)' \
              AND d.name = 'sorts (disk)'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def activeusercount(self):
        """Count of active users"""
        sql = "select to_char(count(*)-1, 'FM99999999999999990') retvalue \
              from v$session where username is not null \
              and status='ACTIVE'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dbsize(self):
        """Size of user data (without temp)"""
        sql = "SELECT to_char(sum(  NVL(a.bytes - NVL(f.bytes, 0), 0)), \
              'FM99999999999999990') retvalue \
              FROM sys.dba_tablespaces d, \
              (select tablespace_name, sum(bytes) bytes from dba_data_files \
              group by tablespace_name) a, \
              (select tablespace_name, sum(bytes) bytes from \
              dba_free_space group by tablespace_name) f \
              WHERE d.tablespace_name = a.tablespace_name(+) AND \
              d.tablespace_name = f.tablespace_name(+) \
              AND NOT (d.extent_management like 'LOCAL' AND d.contents \
              like 'TEMPORARY')"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dbfilesize(self):
        """Size of all datafiles"""
        sql = "select to_char(sum(bytes), 'FM99999999999999990') retvalue \
              from dba_data_files"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def yesterday_incr_size(self):
        """Size of incre_size_per_day kb"""
        sql = """ select  case when increasekb < 0 then 0
            else increasekb end as increasekb
from (select * from (select tmp.usedgb,
         tmp.usedgb - lag(usedgb, 1, null) over(order by s_date) increasekb,
         tmp.s_date
      from (select sub.s_date, sub.usedgb
            from (select t.snap_id,
                         substr(t.rtime, 1, 10) s_date,
                         ROW_NUMBER() OVER(PARTITION BY substr(t.rtime, 1, 10) ORDER BY t.snap_id) rn,
                         ROUND(sum(t.TABLESPACE_USEDSIZE * 8192) /
                               (1024),
                               2) usedgb
                    from SYS.DBA_HIST_TBSPC_SPACE_USAGE t
                   where t.tablespace_id >= 6
                     and to_date(substr(t.rtime, 1, 10), 'mm/dd/yyyy') >
                         trunc(sysdate) - 3
                   group by t.snap_id, substr(t.rtime, 1, 10)) sub
           where rn = 1) tmp) order by s_date desc) where rownum = 1
           
		"""
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]  

    def db_incre_size_per_day(self):
        """Size of db_incre_size_per_day"""
        sql = "select to_char(sum(bytes), 'FM99999999999999990') retvalue \
              from dba_data_files"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
			
    def db_incre_size_per_week(self):
        """Size of db_incre_size_per_week"""
        sql = "select to_char(sum(bytes), 'FM99999999999999990') retvalue \
              from dba_data_files"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]	

    def db_incre_size_per_month(self):
        """Size of db_incre_size_per_month"""
        sql = "select to_char(sum(bytes), 'FM99999999999999990') retvalue \
              from dba_data_files"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]	

    def version(self):
        """Oracle version (Banner)"""
        sql = "select banner from v$version where rownum=1"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def uptime(self):
        """Instance Uptime (seconds)"""
        sql = "select to_char((sysdate-startup_time)*86400, \
              'FM99999999999999990') retvalue from v$instance"
        self.cur.execute(sql)
        res = self.cur.fetchmany(numRows=3)
        for i in res:
            print i[0]

    def commits(self):
        """User Commits"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'user commits'"
        self.cur.execute(sql)
        res = self.cur.fetchmany(numRows=3)
        for i in res:
            print i[0]

    def rollbacks(self):
        """User Rollbacks"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from " \
              "v$sysstat where name = 'user rollbacks'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def deadlocks(self):
        """Deadlocks"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'enqueue deadlocks'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def redowrites(self):
        """Redo Writes"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'redo writes'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def tblscans(self):
        """Table scans (long tables)"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'table scans (long tables)'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def tblrowsscans(self):
        """Table scan rows gotten"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'table scan rows gotten'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def indexffs(self):
        """Index fast full scans (full)"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'index fast full scans (full)'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def hparsratio(self):
        """Hard parse ratio"""
        sql = "SELECT to_char(h.value / t.value * 100, 'FM99999990.9999') retvalue \
              FROM v$sysstat h, v$sysstat t \
              WHERE h.name = 'parse count (hard)' \
              AND t.name = 'parse count (total)'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def netsent(self):
        """Bytes sent via SQL*Net to client"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'bytes sent via SQL*Net to client'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def netresv(self):
        """Bytes received via SQL*Net from client"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'bytes received via SQL*Net from client'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def netroundtrips(self):
        """SQL*Net roundtrips to/from client"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'SQL*Net roundtrips to/from client'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def logonscurrent(self):
        """Logons current"""
        sql = "select to_char(value, 'FM99999999999999990') retvalue from \
              v$sysstat where name = 'logons current'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def lastarclog(self):
        """Last archived log sequence"""
        sql = "select to_char(max(SEQUENCE#), 'FM99999999999999990') \
              retvalue from v$log where archived = 'YES'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def lastapplarclog(self):
        """Last applied archive log (at standby).Next items requires
        [timed_statistics = true]"""
        sql = "select to_char(max(lh.SEQUENCE#), 'FM99999999999999990') \
              retvalue from v$loghist lh, v$archived_log al \
              where lh.SEQUENCE# = al.SEQUENCE# and applied='YES'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def freebufwaits(self):
        """Free buffer waits"""
        sql = "select nvl(to_char(time_waited, 'FM99999999999999990'),'0') retvalue \
              from v$system_event se, v$event_name en \
              where se.event(+) = en.name and en.name = 'free buffer waits'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def bufbusywaits(self):
        """Buffer busy waits"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) = \
              en.name and en.name = 'buffer busy waits'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def logswcompletion(self):
        """log file switch completion"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'log file switch completion'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def logfilesync(self):
        """Log file sync"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en \
              where se.event(+) = en.name and en.name = 'log file sync'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def logprllwrite(self):
        """Log file parallel write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'log file parallel write'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def enqueue(self):
        """Enqueue waits"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en \
              where se.event(+) = en.name and en.name = 'enqueue'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dbseqread(self):
        """DB file sequential read waits"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file sequential read'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dbscattread(self):
        """DB file scattered read"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file scattered read'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dbsnglwrite(self):
        """DB file single write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file single write'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dbprllwrite(self):
        """DB file parallel write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'db file parallel write'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def directread(self):
        """Direct path read"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'direct path read'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def directwrite(self):
        """Direct path write"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'direct path write'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def latchfree(self):
        """latch free"""
        sql = "select to_char(time_waited, 'FM99999999999999990') retvalue \
              from v$system_event se, v$event_name en where se.event(+) \
              = en.name and en.name = 'latch free'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def tablespace(self, name):
        """Get tablespace usage"""
        sql = '''SELECT TABLESPACE_NAME, ROUND(USED_PERCENT, 2)
            FROM DBA_TABLESPACE_USAGE_METRICS
            WHERE TABLESPACE_NAME NOT LIKE '%UNDOTBS%'
            AND TABLESPACE_NAME NOT LIKE '%TEMP%'
            AND TABLESPACE_NAME = '{0}' '''.format(name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[1]

    def tablespace_free(self, name):
        """Get tablespace free size"""
        sql = '''select trunc((tablespace_size - used_space) * 8 / 1024 /1024,2) free_size
             from dba_tablespace_usage_metrics
             where tablespace_name = '{0}' '''.format(name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]


    def show_tablespaces(self):
        """List tablespace names in a JSON like format for Zabbix use"""
        sql = """SELECT tablespace_name FROM dba_tablespaces 
            where TABLESPACE_NAME NOT in (select value from v$parameter where name='undo_tablespace')
            AND TABLESPACE_NAME NOT in (select tablespace_name from dba_temp_files)
			ORDER BY 1"""
        self.cur.execute(sql)
        res = self.cur.fetchall()
        key = ['{#TABLESPACE}']
        lst = []
        for i in res:
            d = dict(zip(key, i))
            lst.append(d)
        print json.dumps({'data': lst})

    def show_tablespaces_undo(self):
        """List tablespace names in a JSON like format for Zabbix use"""
        sql = "SELECT tablespace_name FROM dba_tablespaces where TABLESPACE_NAME LIKE '%UNDOTBS%' ORDER BY 1"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        key = ['{#TABLESPACE_UNDO}']
        lst = []
        for i in res:
            d = dict(zip(key, i))
            lst.append(d)
        print json.dumps({'data': lst})

    def tablespace_undo(self, name):
        """Get tablespace usage"""
        sql = '''SELECT  A.TABLESPACE_NAME ,
            TRUNC((A.USED / B.TOTAL), 2)
            FROM (SELECT TABLESPACE_NAME, SUM(BYTES) / 1024 / 1024 USED
            FROM DBA_UNDO_EXTENTS
            WHERE STATUS = 'ACTIVE'
            GROUP BY TABLESPACE_NAME) A,
            (SELECT TABLESPACE_NAME, TABLESPACE_SIZE * 8 / 1024 TOTAL
            FROM DBA_TABLESPACE_USAGE_METRICS
            WHERE TABLESPACE_NAME LIKE '%UNDOTBS%') B
            WHERE A.TABLESPACE_NAME = B.TABLESPACE_NAME
            AND A.TABLESPACE_NAME = '{0}' '''.format(name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        count = self.cur.rowcount
        if count==0:
           print 0
        for i in res:
            print i[1]

    def show_tablespaces_temp(self):
        """List temporary tablespace names in a JSON like
        format for Zabbix use"""
        sql = "select distinct TABLESPACE_NAME from dba_temp_files"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        key = ['{#TABLESPACE_TEMP}']
        lst = []
        for i in res:
            d = dict(zip(key, i))
            lst.append(d)
        print json.dumps({'data': lst})

    def check_archive(self, archive):
        """List archive used"""
        sql = "select trunc((total_mb-free_mb)*100/(total_mb)) PCT from \
              v$asm_diskgroup_stat where name='{0}' \
              ORDER BY 1".format(archive)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def show_asm_volumes(self):
        """List als ASM volumes in a JSON like format for Zabbix use"""
        sql = "select NAME from v$asm_diskgroup_stat ORDER BY 1"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        key = ['{#ASMVOLUME}']
        lst = []
        for i in res:
            d = dict(zip(key, i))
            lst.append(d)
        print json.dumps({'data': lst})

    def asm_volume_use(self, name):
        """Get ASM volume usage"""
        sql = "select round(((TOTAL_MB-FREE_MB)/TOTAL_MB*100),2) from \
              v$asm_diskgroup_stat where name = '{0}'".format(name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def asm_free_size(self, name):
        """Get ASM volume free size"""
        sql = "select trunc(FREE_MB/1024,2) from v$asm_diskgroup_stat where name = '{0}'".format(name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def query_lock(self):
        """Query lock"""
        sql = "SELECT /*+rule*/ count(*) FROM v$lock l WHERE  block=1"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def query_redologs(self):
        """Redo logs"""
        sql = "select COUNT(*) from v$LOG WHERE STATUS='ACTIVE'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def query_rollbacks(self):
        """Query Rollback"""
        sql = "select nvl(trunc(sum(used_ublk*4096)/1024/1024),0) from \
              v$transaction t,v$session s where ses_addr = saddr"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def query_sessions(self):
        """Query Sessions"""
        sql = "select count(*) from v$session where username is not null \
              and status='ACTIVE'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def query_maxprocess(self):
        """Query max process"""
        sql = "select value from v$parameter where name='processes'"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def query_cursession(self):
        """Query current sessions"""
        sql = "select count(0) from v$session"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]


    def tablespace_temp(self, name):
        """Query temporary tablespaces"""
        sql = "SELECT TRUNC((A.USED / B.TOTAL), 2) * 100 \
             FROM (SELECT TABLESPACE, SUM((BLOCKS * 8) / 1024) USED \
             FROM V$TEMPSEG_USAGE \
             GROUP BY TABLESPACE) A, \
             (SELECT TABLESPACE_NAME, SUM(BYTES / 1024 / 1024) TOTAL \
             FROM DBA_TEMP_FILES WHERE TABLESPACE_NAME = '{0}' \
             GROUP BY TABLESPACE_NAME) B \
             WHERE A.TABLESPACE = B.TABLESPACE_NAME".format(name)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        count = self.cur.rowcount
        if count==0:
           print 0
        for i in res:
            print i[0]

    def query_sysmetrics(self, name):
        """Query v$sysmetric parameters"""
        sql = "select value from v$sysmetric where METRIC_NAME ='{0}' and \
              rownum <=1 order by INTSIZE_CSEC desc".format(name.replace('_', ' '))
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def query_waitms(self, name):
        """Query waitevent delay"""
        sql = "SELECT TRUNC(E.TIME_WAITED * 10 / (CASE \
               WHEN WAIT_COUNT = 0 THEN \
               1 \
               ELSE \
               WAIT_COUNT \
               END), \
               4) WAIT_MS \
              FROM V$EVENTMETRIC E \
             WHERE EVENT_ID = \
            (SELECT EVENT_ID FROM V$EVENT_NAME WHERE NAME = '{0}')".format(name.replace('_', ' '))
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def query_wait_class(self, name):
        """Query waitevent class"""
        sql = "SELECT SUM(TOTAL_WAITS) \
             FROM V$SYSTEM_EVENT \
             WHERE WAIT_CLASS = '{0}'".format(name.replace('_', ' '))
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def fra_use(self):
        """Query the Fast Recovery Area usage"""
        sql = "select round((SPACE_LIMIT-(SPACE_LIMIT-SPACE_USED))/ \
              SPACE_LIMIT*100,2) FROM V$RECOVERY_FILE_DEST WHERE SPACE_LIMIT<>0"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def show_users(self):
        """Query the list of users on the instance"""
        sql = "SELECT username FROM dba_users ORDER BY 1"
        self.cur.execute(sql)
        res = self.cur.fetchall()
        key = ['{#DBUSER}']
        lst = []
        for i in res:
            d = dict(zip(key, i))
            lst.append(d)
        print json.dumps({'data': lst})

    def user_status(self, dbuser):
        """Determines whether a user is locked or not"""
        sql = "SELECT account_status FROM dba_users WHERE username='{0}'" \
            .format(dbuser)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        if res ==[]:
           res = ['OPEN']
           print res[0]
        else:
           for i in res:
               print i[0]


    def query_sysstat(self, name):
        """Query sysstat"""
        sql = "select value from v$sysstat \
               where name = '{0}' ".format(name.replace('_', ' '))
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def lgwr_wait(self):
        """Query lgwr wait"""
        sql = """ SELECT sum(SECONDS_IN_WAIT) FROM V$SESSION WHERE PROGRAM LIKE '%(LGWR)%' """
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def forbidden_login(self,osusr):
        """monitor forbidden login"""
        sql = """select osuser
              from (select LISTAGG(tt, ',') WITHIN GROUP(ORDER BY tt) osuser
              from (select osuser||' from '||machine||' connect dbuser '||username tt 
                  from v$session
                 where status <> 'KILLED' and machine <> 'D21107U34-61-103' and machine not in (select host_name from v$instance)
                   and (program like '%sqlplus@%'
                   or program in ('plsqldev.exe'))
                   and osuser not in ({0})
                 group by osuser||' from '||machine||' connect dbuser '||username))
             where osuser is not null""".format("'"+"','".join(osusr.split(","))+"'")
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]	     
    
    def sequence_percent(self,percent):
        """monitor sequence used percent"""
        sql = """select nvl(LISTAGG(sequence_owner || '.' || sequence_name, ',') WITHIN GROUP(ORDER BY sequence_owner || '.' || sequence_name),'none') text1
                  from dba_sequences
                 where SEQUENCE_OWNER not in ('ANONYMOUS',
                                              'APEX_030200',
                                              'APEX_PUBLIC_USER',
                                              'APPLSYS',
                                              'CTXSYS',
                                              'DBSNMP',
                                              'DIP',
                                              'DMSYS',
                                              'EXFSYS',
                                              'FLOWS_040100',
                                              'FLOWS_FILES',
                                              'HR',
                                              'IX',
                                              'LBACSYS',
                                              'MDDATA',
                                              'MDSYS',
                                              'MGMT_VIEW',
                                              'OE',
                                              'OLAPSYS',
                                              'ORACLE_OCM',
                                              'ORDDATA',
                                              'ORDPLUGINS',
                                              'ORDSYS',
                                              'OUTLN',
                                              'PERFSTAT',
                                              'QCOAGT',
                                              'SI_INFORMTN_SCHEMA',
                                              'SPATIAL_CSW_ADMIN_USR',
                                              'SPATIAL_WFS_ADMIN_USR',
                                              'SYS',
                                              'SYSMAN',
                                              'SYSTEM',
                                              'WK_TEST',
                                              'WKPROXY',
                                              'WKSYS',
                                              'WMSYS',
                                              'XDB')
                   and CYCLE_FLAG = 'N'
                   and round(last_number / max_value, 2) * 100 > {0}""".format(percent)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none'
        for i in res:
            print i[0]
   
    def dg_standby(self):
        """monitor dataguard sync"""
        sql = """select 'DG Standby库延迟告警：' || a.name || ':' || a.value || ',' || b.name || ':' ||
            b.value || ',' || c.name || ':' || c.value rval
            from V$DATAGUARD_STATS a, V$DATAGUARD_STATS b, V$DATAGUARD_STATS c
            where a.name = 'transport lag'
            and b.name = 'apply lag'
            and c.name = 'apply finish time'
            and (a.value >= '+00 30:00:00' or b.value >= '+00 30:00:00' or
            c.value >= '+00 30:00:00.000')"""
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]
            
    def waitevent(self):
        """monitor waitevent"""
        sql = '''SELECT '数据库等待事件监控告警(' || TO_CHAR(SYSDATE, 'YYYYMMDD HH24MISS') ||
            ')：等待事件：' || EVENT || '，类型：' || A.WAIT_CLASS || '，实例:' ||
            INST_ID || '，数量：' || NUM || '，恐影响生产业务，请尽快处理！(持久化组监控)'
            FROM (SELECT INST_ID, EVENT, WAIT_CLASS, COUNT(0) NUM
            FROM V$SESSION
            WHERE WAIT_CLASS <> 'Idle'
            GROUP BY INST_ID, EVENT, WAIT_CLASS) A
            WHERE A.NUM >= 30'''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]
            
    def backup(self):
        """monitor backup"""
        sql = '''SELECT 
            '数据库备份异常告警(' || TO_CHAR(SYSDATE, 'YYYYMMDD HH24MISS') || ')：类型：' ||
            INPUT_TYPE || ',状态:' || STATUS || ',备份开始时间:' ||
            TO_CHAR(START_TIME, 'YYYY-MM-DD HH24:MI:SS') ||
            '；请尽快联系其相关责任人确认！(持久化组监控)'
            FROM V$RMAN_BACKUP_JOB_DETAILS B
            WHERE START_TIME = (SELECT MAX(START_TIME) FROM V$RMAN_BACKUP_JOB_DETAILS)
            AND STATUS IN ('FAILED', 'COMPLETED WITH ERRORS', 'RUNNING WITH ERRORS')'''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]
        
            
    def asmused(self):
        """monitor asm diskgroup"""
        sql = '''select '数据库ASM磁盘组告警(' || to_char(sysdate, 'yyyymmdd hh24miss')    
            ||'):'||a.NAME||'总大小'||a.TOTAL_MB/1024||'G,使用率'||round((a.TOTAL_MB-a.FREE_MB)/a.TOTAL_MB*100,2)||
            '%,请速度查看数据库，以免影响生产业务！(持久化组监控)'
            from v$asm_diskgroup a where round((a.TOTAL_MB-a.FREE_MB)/a.TOTAL_MB*100,2)>=90'''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]
            
    def dbmsjobs(self):
        """monitor dbms jobs"""
        sql = '''select '数据库平台JOB运行失败告警(' || to_char(sysdate, 'yyyymmdd hh24miss') ||
            ')：JOB_ID：' || job || ',FAILURES:' || failures || ',SCHEMA:' ||
            schema_user || ',LAST_DATE:' || last_date || ',NEXT_DATE:' ||
            next_date || ',WHAT:' || what || '；请尽快联系其相关责任人确认！(持久化组监控)'
            from dba_jobs
            where failures <> 0
            and broken <> 'Y' '''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]
            
    def undotablespace(self):
        """monitor undo tablespace"""
        sql = '''SELECT '数据库平台UNDO表空间监控告警(' || TO_CHAR(SYSDATE, 'yyyymmdd hh24miss') || ')：' ||
            A.TABLESPACE_NAME || '使用率已达' ||
            TRUNC((A.USED / B.TOTAL), 2) * 100 || '%' ||
            '），请尽快查看当前UNDO使用情况，以免影响生产业务！(持久化组监控)'
            FROM (SELECT TABLESPACE_NAME, SUM(BYTES) / 1024 / 1024 USED
            FROM DBA_UNDO_EXTENTS
            WHERE STATUS = 'ACTIVE'
            GROUP BY TABLESPACE_NAME) A,
            (SELECT TABLESPACE_NAME, TABLESPACE_SIZE * 8 / 1024 TOTAL
            FROM DBA_TABLESPACE_USAGE_METRICS
            WHERE TABLESPACE_NAME LIKE '%UNDOTBS%') B
            WHERE A.TABLESPACE_NAME = B.TABLESPACE_NAME
            AND TRUNC((A.USED / B.TOTAL), 2) >= 0.60'''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]
            
    def temptablespace(self):
        """monitor temp tablespace"""
        sql = '''SELECT '数据库平台TEMP表空间监控告警(' || TO_CHAR(SYSDATE, 'yyyymmdd hh24miss') || ')：' ||
            A.TABLESPACE || '使用率已达' || TRUNC((A.USED / B.TOTAL), 2) * 100 || '%' ||
            '），请尽快查看当前TEMP使用情况，以免影响生产业务！(持久化组监控)'
            FROM (SELECT tablespace, sum((blocks * 8) / 1024) used
            FROM V$TEMPSEG_USAGE
            group by tablespace) A,
            (SELECT TABLESPACE_NAME, TABLESPACE_SIZE * 8 / 1024 TOTAL
            FROM DBA_TABLESPACE_USAGE_METRICS
            WHERE TABLESPACE_NAME LIKE '%TEMP%') B
            WHERE A.TABLESPACE = B.TABLESPACE_NAME
            AND TRUNC((A.USED / B.TOTAL), 2) >= 0.60'''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]

    def unusableindex(self):
        """monitor unusableindex"""
        sql = """ select wm_concat(unsuable_index) from  (select  owner||':'||LISTAGG(index_name, ',') WITHIN GROUP (ORDER BY index_name)||chr(13) as unsuable_index
 from
 (select DISTINCT t1.index_owner owner,t1.index_name from dba_ind_partitions t1 where t1.status='UNUSABLE'
 union all
 select DISTINCT t2.owner,t2.index_name  from dba_indexes t2 where t2.status='UNUSABLE')
 where owner not in ('BPDBMONITOR','SYS','SYSTEM','ORAMAINTAIN','APPADMIN','SCOTT',
'GOLDENGATE',
'OUTLN',
'MGMT_VIEW',
'FLOWS_FILES',
'MDSYS',
'ORDSYS',
'EXFSYS',
'DBSNMP',
'WMSYS',
'APPQOSSYS',
'APEX_030200',
'OWBSYS_AUDIT',
'ORDDATA',
'CTXSYS',
'ANONYMOUS',
'SYSMAN',
'XDB',
'ORDPLUGINS',
'OWBSYS',
'SI_INFORMTN_SCHEMA',
'OLAPSYS',
'ORACLE_OCM',
'XS$NULL',
'MDDATA',
'IX',
'SH',
'DIP',
'OE',
'APEX_PUBLIC_USER',
'HR',
'SPATIAL_CSW_ADMIN_USR',
'SPATIAL_WFS_ADMIN_USR',
'AUDSYS',
'DMSYS',
'DVF',
'DVSYS',
'EXDSYS',
'GSMADMIN_INTERNAL',
'GSMCATUSER',
'GSMUSER',
'LBACSYS',
'MTSSYS',
'ODM',
'ODM_MTR',
'OJVMSYS',
'SYSBACKUP',
'SYSDG',
'SYSKM',
'TSMSYS',
'WKPROXY',
'WKSYS',
'WK_TEST',
'XTISYS',
'AURORA$JIS$UTILITY$',
'AURORA$ORB$UNAUTHENTICATED',
'DSSYS',
'OSE$HTTP$ADMIN',
'PERFSTAT','REPADMIN','ITSM','ITSM2')

group by owner)
		"""
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]

    def tablespaceused(self):
        """monitor tablespace used"""
        sql = '''select '数据库平台表空间(' || to_char(sysdate, 'yyyymmdd hh24miss') || ')' ||
            tablespace_name || '使用率已达' || trunc(used_percent, 2) || '%' ||
            '(表空间总大小：' || tablespace_size * 8 / 1024 / 1024 || 'G，已使用空间大小：' ||
            trunc(used_space * 8 / 1024 / 1024, 2) ||
            'G），请尽快通知运维组扩充该表空间，以免影响生产业务！(持久化组监控)'
            from dba_tablespace_usage_metrics
            where TABLESPACE_NAME NOT LIKE '%UNDOTBS%'
            AND TABLESPACE_NAME NOT LIKE '%TEMP%'
            AND used_percent >= 80'''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        #print res
        count = self.cur.rowcount
        if count==0:
           print 'none' 
        for i in res:
            print i[0]

    def pga_aggregate_target(self):
        """check pga_aggregate_target parameter"""
        sql = "select to_char(decode(unit, 'bytes', value / 1024 / 1024, value), \
            '999999999.9') value \
            from V$PGASTAT \
            where name in 'aggregate PGA target parameter'" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def pga_in_use(self):
        """check pga used"""
        sql = "select to_char(decode(unit, 'bytes', value / 1024 / 1024, value), \
            '999999999.9') value \
            from V$PGASTAT \
            where name in 'total PGA inuse'" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def pool_dict_cache(self):
        """check pool_dict_cache"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            'shared pool', \
            decode(name, \
            'dictionary cache', \
            (bytes) / (1024 * 1024), \
            0), \
            0)), \
            2)) pool_dict_cache \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def pool_free_mem(self):
        """check pool_free_mem"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            'shared pool', \
            decode(name, \
            'free memory', \
            (bytes) / (1024 * 1024), \
            0), \
            0)), \
            2)) pool_free_mem \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
            
    def pool_lib_cache(self):
        """check pool_lib_cache"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            'shared pool', \
            decode(name, \
            'library cache', \
            (bytes) / (1024 * 1024), \
            0), \
            0)), \
            2)) pool_lib_cache \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def pool_misc(self):
        """check pool_misc"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            'shared pool', \
            decode(name, \
            'library cache', \
            0, \
            'dictionary cache', \
            0, \
            'free memory', \
            0, \
            'sql area', \
            0, \
            (bytes) / (1024 * 1024)), \
            0)), \
            2)) pool_misc \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def pool_sql_area(self):
        """check pool_sql_area"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            'shared pool', \
            decode(name, \
            'sql area', \
            (bytes) / (1024 * 1024), \
            0), \
            0)), \
            2)) pool_sql_area \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
            
            
    def sga_buffer_cache(self):
        """check sga_buffer_cache"""
        sql = "SELECT to_char(ROUND(SUM(decode(pool, \
            NULL, \
            decode(name, \
            'db_block_buffers', \
            (bytes) / (1024 * 1024), \
            'buffer_cache', \
            (bytes) / (1024 * 1024), \
            0), \
            0)), \
            2)) sga_bufcache \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def sga_fixed(self):
        """check sga_fixed"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            NULL, \
            decode(name, \
            'fixed_sga', \
            (bytes) / (1024 * 1024), \
            0), \
            0)), \
            2)) sga_fixed \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def sga_java_pool(self):
        """check sga_java_pool"""
        sql = "SELECT to_char(ROUND(SUM(decode(pool, \
            'java pool', \
            (bytes) / (1024 * 1024), \
            0)), \
            2)) sga_jpool \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
            
    def sga_large_pool(self):
        """check sga_large_pool"""
        sql = "SELECT to_char(ROUND(SUM(decode(pool, \
            'large pool', \
            (bytes) / (1024 * 1024), \
            0)), \
            2)) sga_lpool \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def sga_log_buffer(self):
        """check sga_log_buffer"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            NULL, \
            decode(name, \
            'log_buffer', \
            (bytes) / (1024 * 1024), \
            0), \
            0)), \
            2)) sga_lbuffer \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
    def sga_shared_pool(self):
        """check sga_shared_pool"""
        sql = "SELECT TO_CHAR(ROUND(SUM(decode(pool, \
            'shared pool', \
            decode(name, \
            'library cache', \
            0, \
            'dictionary cache', \
            0, \
            'free memory', \
            0, \
            'sql area', \
            0, \
            (bytes) / (1024 * 1024)), \
            0)), \
            2)) pool_misc \
            FROM V$SGASTAT" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
            
            
    def blocking_session(self):
        """blocking_session"""
        sql = "select /*+rule*/ count(0) from v$lock where request<>0" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def parallel_session(self):
        """parallel_session"""
        sql = "select count(0) from v$px_session" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]
    def sql_elapsed_time(self,val1,val2):
        """Get sql execute time"""
        sql = '''select sql_id||'##'||avg_time1 AS avg_time1
           from (select sql_id,
		          case when avg_time1 <1 and avg_time1 >0 then to_char(avg_time1, '0.000')
				  else to_char(avg_time1)
				  end as avg_time1 from 
			(select distinct round((elapsed_time / case
                 when executions = 0 then
                  1
                 else
                  executions
               end / 1000000),3) avg_time1,sql_id
           from v$sql
           where last_active_time > sysdate - 10/1440
                 and SQL_TEXT not like '/* SQL Analyze(1) */%'
                 and ((SQL_TEXT not like '/* SQL Analyze(1) */%') and (SQL_TEXT not like '%T\_CUSTOMER\_PASSWORD%' escape nchr(92)))
                 and PARSING_SCHEMA_NAME not in 
('BPDBMONITOR','SYS','SYSTEM','ORAMAINTAIN','APPADMIN','SCOTT',
'GOLDENGATE',
'OUTLN',
'MGMT_VIEW',
'FLOWS_FILES',
'MDSYS',
'ORDSYS',
'EXFSYS',
'DBSNMP',
'WMSYS',
'APPQOSSYS',
'APEX_030200',
'OWBSYS_AUDIT',
'ORDDATA',
'CTXSYS',
'ANONYMOUS',
'SYSMAN',
'XDB',
'ORDPLUGINS',
'OWBSYS',
'SI_INFORMTN_SCHEMA',
'OLAPSYS',
'ORACLE_OCM',
'XS$NULL',
'MDDATA',
'IX',
'SH',
'DIP',
'OE',
'APEX_PUBLIC_USER',
'HR',
'SPATIAL_CSW_ADMIN_USR',
'SPATIAL_WFS_ADMIN_USR',
'AUDSYS',
'DMSYS',
'DVF',
'DVSYS',
'EXDSYS',
'GSMADMIN_INTERNAL',
'GSMCATUSER',
'GSMUSER',
'LBACSYS',
'MTSSYS',
'ODM',
'ODM_MTR',
'OJVMSYS',
'SYSBACKUP',
'SYSDG',
'SYSKM',
'TSMSYS',
'WKPROXY',
'WKSYS',
'WK_TEST',
'XTISYS',
'AURORA$JIS$UTILITY$',
'AURORA$ORB$UNAUTHENTICATED',
'DSSYS',
'OSE$HTTP$ADMIN',
'PERFSTAT','REPADMIN','ITSM','ITSM2'))
		   where avg_time1 between '{0}' and '{1}'
		   	order by to_number(avg_time1) desc) '''.format(val1,val2)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def low_sql(self):
        """Get low sql"""
        sql = '''select count(0)
              from (select buffer_gets / (case
                 when executions = 0 then
                  1
                 else
                  executions
               end) avg_gets,
               (elapsed_time / case
                 when executions = 0 then
                  1
                 else
                  executions
               end / 1000000) avg_time,executions
            from v$sql
            where executions>=10 and first_load_time >=
               to_char((sysdate - 10 / 1440), 'yyyy-mm-dd/hh24:mi:ss'))
            where avg_gets >= 100000 and avg_time>=0.1'''
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]


    def shared_pool_sub(self, num):
        """Check shared_pool_sub"""
        sql = '''SELECT ROUND(SUM(BYTES) / 1048576, 2) free_mb
                FROM (SELECT DECODE(TO_CHAR(ksmdsidx), '0', '0 - Unused', ksmdsidx) subpool,
               ksmssnam NAME,
               ksmsslen BYTES
               FROM x$ksmss
              WHERE ksmsslen > 0
              AND LOWER(ksmssnam) LIKE LOWER('%free memory%'))
              where subpool= '{0}'
              GROUP BY subpool, NAME '''.format(num)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def dg_standby_delay(self):
        """dg_standby_delay"""
        sql = "SELECT round((to_date(to_char(systimestamp, 'yyyy-mm-dd hh24:mi:ss'), \
            'yyyy-mm-dd hh24:mi:ss') - \
            to_date(to_char(scn_to_timestamp(current_scn), \
            'yyyy-mm-dd hh24:mi:ss'), \
            'yyyy-mm-dd hh24:mi:ss')) * 24 * 60) gap_min \
            FROM v$database" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def monitor_hard_parse(self,value):
        """monitor_hard_parse"""
        sql = "select case when LISTAGG('sid' || session_id || 'serial#' || SESSION_SERIAL#,',') WITHIN GROUP (ORDER BY 'sid' || session_id || 'serial#' || SESSION_SERIAL#) is null  \
            then 'none' else LISTAGG('sid' || session_id || 'serial#' || SESSION_SERIAL#,',') WITHIN GROUP (ORDER BY 'sid' || session_id || 'serial#' || SESSION_SERIAL#) \
            end as text1 \
            from (select t.SESSION_ID, t.SESSION_SERIAL#, count(*)  \
            from v$active_session_history t  \
            where t.IN_HARD_PARSE = 'Y' \
            and t.IN_PARSE = 'Y'  \
            and t.IN_SQL_EXECUTION = 'N' \
            and t.SAMPLE_TIME >= sysdate - {0} / 1440  \
            group by t.SESSION_ID, t.SESSION_SERIAL# \
            having count(*) >= {0}*60 - 60)".format(value)
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]

    def db_time(self):
        """DB_TIME"""
        sql = "SELECT VALUE FROM V$SYSSTAT WHERE NAME = 'DB time'" 
        self.cur.execute(sql)
        res = self.cur.fetchall()
        for i in res:
            print i[0]            
            
                     
class Main(Checks):
    def __init__(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--username')
        parser.add_argument('--password')
        parser.add_argument('--address')
        parser.add_argument('--database')

        subparsers = parser.add_subparsers()

        for name in dir(self):
            if not name.startswith("_"):
                p = subparsers.add_parser(name)
                method = getattr(self, name)
                argnames = inspect.getargspec(method).args[1:]
                for argname in argnames:
                    p.add_argument(argname)
                p.set_defaults(func=method, argnames=argnames)
        self.args = parser.parse_args()

    def db_connect(self):
        a = self.args
        username = a.username
        password = a.password
        address = a.address
        database = a.database
        self.db = cx_Oracle.connect("{0}/{1}@{2}/{3}".format(
            username, password, address, database))
        self.cur = self.db.cursor()

    def db_close(self):
        self.db.close()

    def __call__(self):
        try:
            a = self.args
            callargs = [getattr(a, name) for name in a.argnames]
            self.db_connect()
            try:
                return self.args.func(*callargs)
            finally:
                self.db_close()
        except Exception, err:
            print 0
            print str(err)

if __name__ == "__main__":
    main = Main()
    main()

