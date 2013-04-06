# -*- coding: utf-8 -*-

import sys
sys.path.append('snsaspi')
import snsapi
from snsapi.utils import Serialize
from snsapi.snslog import SNSLog as logger
from snsapi import snstype

import base64
import hashlib
import sqlite3
import time

class Queue(object):
    def __init__(self, url = "message.db"):
        self.url = url

    def _create_schema(self):
        cur = self.con.cursor()
        try:
            cur.execute("create table meta (time integer, path text)")
            cur.execute("insert into meta values (?,?)", (int(time.time()), self.url))
            self.con.commit()
        except sqlite3.OperationalError, e:
            if e.message == "table meta already exists":
                return 
            else:
                raise e
    
        cur.execute("""
        CREATE TABLE msg (
        id INTEGER PRIMARY KEY, 
        time INTEGER, 
        text TEXT,
        userid TEXT, 
        username TEXT, 
        mid TEXT, 
        platform TEXT, 
        digest TEXT, 
        digest_parsed TEXT, 
        digest_pyobj TEXT, 
        parsed TEXT, 
        pyobj TEXT, 
        flag TEXT, 
        weight FLOAT, 
        weight_time INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE tag (
        id INTEGER PRIMARY KEY, 
        name INTEGER, 
        visible INTEGER,
        parent INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE msg_tag (
        id INTEGER PRIMARY KEY, 
        msg_id INTEGER,  
        tag_id INTEGER
        )
        """)

        cur.execute("""
        CREATE TABLE log (
        id INTEGER PRIMARY KEY, 
        time TEXT,  
        operation TEXT
        )
        """)

        self.con.commit()

    def log(self, text):
        cur = self.con
        cur.execute("INSERT INTO log(time,operation) VALUES (?,?)", (int(time.time()), text))
        self.con.commit()
        
    def connect(self):
        '''
        Connect to SQLite3 database and create cursor. 
        Also initialize the schema if necessary. 

        '''
        url = self.url
        # Disable same thread checking. 
        # SQLite3 can support multi-threading. 
        # http://stackoverflow.com/questions/393554/python-sqlite3-and-concurrency
        self.con = sqlite3.connect(url, check_same_thread = False)
        self.con.isolation_level = None
        self._create_schema()

    def _pyobj2str(self, message):
        return base64.encodestring(Serialize.dumps(message))

    def _str2pyobj(self, message):
        return Serialize.loads(base64.decodestring(message))

    def _digest_pyobj(self, message):
        return hashlib.sha1(self._pyobj2str(message)).hexdigest()

    def _weight_feature(self, message):
        # A dummy method just to conform to SNSRouter schema
        return 0

    def _inqueue(self, message):
        cur = self.con.cursor()
        try:
            # Deduplicate
            # Explain the problem of the following two methods for future reference:
            # 1. digest = self._digest_pyobj(message)
            #    Python object are hashed to different values even the SNS message 
            #    fields are all the same. 
            # 2. digest = message.digest_parsed()
            #    I forget what is the problem.. I should have noted before. 
            digest = message.digest()
            #logger.debug("message pyobj digest '%s'", digest)
            r = cur.execute('''
            SELECT digest FROM msg
            WHERE digest = ?
            ''', (digest, ))

            if len(list(r)) > 0:
                #logger.debug("message '%s' already exists", digest)
                return False
            else:
                logger.debug("message '%s' is new", digest)

            #TODO:
            #    This is temporary solution for object digestion. 
            #   
            #    For our Message object, the following evaluates to False!!
            #    Serialize.dumps(o) == Serialize.dumps(Serialize.loads(Serialize.dumps(o)))
            #
            #    To perform deduplication and further refer to this message, 
            #    we store the calculated digestion as an attribute of the message. 
            #    Note however, after this operation the digest of 'message' will not 
            #    be the valued stored therein! This is common problem in such mechanism, 
            #    e.g. UDP checksum. Developers should have this in mind. 
            message.digest_pyobj = self._digest_pyobj(message)

            cur.execute('''
            INSERT INTO msg(
            time , 
            text ,
            userid , 
            username , 
            mid , 
            platform , 
            digest , 
            digest_parsed , 
            digest_pyobj , 
            parsed , 
            pyobj , 
            flag , 
            weight ,
            weight_time
            )
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            ''', (\
                    message.parsed.time,\
                    message.parsed.text,\
                    message.parsed.userid,\
                    message.parsed.username,\
                    str(message.ID),\
                    message.platform,\
                    message.digest(),\
                    message.digest_parsed(),\
                    #self._digest_pyobj(message),\
                    message.digest_pyobj,\
                    message.dump_parsed(),\
                    self._pyobj2str(message),\
                    "unseen", 
                    self._weight_feature(message),
                    int(time.time())
                    ))
            return True
        except Exception, e:
            logger.warning("failed: %s", str(e))
            #print message
            #raise e
            return False

    #def _home_timeline(self, channel):
    #    return self.sp.home_timeline(channel=channel)

    def input(self, ml):
        count = 0 
        for m in ml:
            if self._inqueue(m):
                count += 1
        logger.info("Input %d new message", count)
        self.log("Input %d new message" % count)

    def get_unseen_count(self):
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT count(*) FROM msg  
        WHERE flag='unseen'
        ''')
        
        try:
            return r.next()[0]
        except Exception, e:
            logger.warning("Catch Exception: %s", e)
            return -1

    def output(self, count = 20):
        cur = self.con.cursor()
        
        r = cur.execute('''
        SELECT id,time,userid,username,text,pyobj,weight FROM msg  
        WHERE flag='unseen'
        ORDER BY time DESC LIMIT ?
        ''', (count,))

        message_list = snstype.MessageList()
        for m in r:
            obj = self._str2pyobj(m[5])
            obj.msg_id = m[0]
            obj.weight = m[6]
            message_list.append(obj)

        return message_list

    def select_digest(self, digest):
        condition = "digest='" + digest + "'"
        return self.select(condition)

    def select_userid(self, userid, count=None):
        condition = "userid='" + str(userid) + "'"
        return self.select(condition, count)

    def select_username(self, username, count=None):
        condition = "username LIKE '%" + username + "%'"
        return self.select(condition, count)

    def select_text(self, text, count=None):
        '''
        Select messages that contain certain text
        '''
        condition = "text LIKE '%" + text + "%'"
        return self.select(condition, count)

    def select(self, condition, count=None):
        '''
        Select messages from 'msg' table alone and return SNSApi's MessageList
        '''
        qs = "SELECT DISTINCT msg.id,msg.pyobj FROM msg WHERE %s" % condition
        if count:
            qs += "ORDER BY rowid DESC LIMIT " + str(count)
        return self.sql(qs)

    def sql(self, query_string):
        cur = self.con.cursor()
        try:
            r = cur.execute(query_string)
            logger.debug("SQL query string: %s", query_string)

            message_list = snstype.MessageList()
            for m in r:
                obj = self._str2pyobj(m[1])
                obj.msg_id = m[0]
                message_list.append(obj)
            return message_list
        except Exception, e:
            logger.warning("Catch exception when executing '%s': %s", query_string, e)
            return snstype.MessageList()

    def flag(self, message, fl):
        '''
        flag v.s. message: 1 <-> 1

        '''
        if isinstance(message, snstype.Message):
            #digest = message.digest_pyobj
            msg_id = message.msg_id
        else:
            msg_id = message

        cur = self.con.cursor()

        ret = False
        try:
            cur.execute('''
            UPDATE msg
            SET flag=?
            WHERE id=?
            ''', (fl, msg_id))
            self.con.commit()
            ret = True
        except Exception, e:
            logger.warning("Catch exception: %s", e)

        self.log("[flag]%s;%s;%s" % (msg_id, fl, ret))
        return ret

    def tag_toggle(self, tag_id):
        cur_visible = self.tags_all[tag_id]['visible']
        cur = self.con.cursor()
        r = cur.execute('''
        UPDATE tag
        SET visible=?
        WHERE id=?
        ''', (1 - cur_visible, tag_id))
        logger.debug("Set tag %d to visibility %d", tag_id, 1 - cur_visible)
        self.refresh_tags()

    def tag_add(self, name):
        cur = self.con.cursor()
        r = cur.execute('''
        INSERT INTO tag(name, visible)
        VALUES(?, ?)
        ''', (name, 1))
        logger.debug("Add tag %s", name)
        self.refresh_tags()

    def get_tags(self):
        '''
        Only return visible tags

        '''
        return self.tags_visible

    def get_all_tags(self):
        return self.tags_all

    def refresh_tags(self):
        self.tags_all = {}
        self.tags_visible = {}
        cur = self.con.cursor()
        r = cur.execute('''
        SELECT id,name,visible,parent FROM tag  
        ''')
        for t in cur:
            self.tags_all[t[0]] = {
                    "id": t[0],
                    "name": t[1], 
                    "visible": t[2],
                    "parent": t[3], 
                    }
            if t[2] == 1:
                self.tags_visible[t[0]] = t[1]

    def tag(self, message, tg):
        '''
        flag v.s. message: * <-> *

        '''
        if isinstance(message, snstype.Message):
            msg_id = message.msg_id
        else:
            msg_id = message

        cur = self.con.cursor()

        ret = False
        try:
            cur.execute('''
            INSERT INTO msg_tag(msg_id, tag_id)
            VALUES (?,?)
            ''', (msg_id, tg))
            self.con.commit()
            ret = True
        except Exception, e:
            logger.warning("Catch exception: %s", e)

        self.log("[tag]%s;%s;%s" % (msg_id, tg, ret))
        return ret

if __name__ == '__main__':
    q = Queue()
    q.connect()
    print q.output(1)
