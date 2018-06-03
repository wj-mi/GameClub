# -*- coding:utf-8 -*-
"""俱乐部管理
"""
import json
import time
import gameDataInterface

from util.gameLog import gameLog
import Singleton
import gameDataInterface
from protocol import *
from club import GameClub
from utils.generate_uuid import compress_uuid
from utils.gameError import GameException, new_cur


class ClubManager(Singleton.Singleton):

    def __init__(self):
        super(AccountManager,self).__init__()
        self._slave = None
        """服务器启动时加载一次,读取所有的club到内存中"""
        # _clubs (dict)k: v==> club_uuid: club object
        self._clubs = self.prepare_clubs()
    
    def setSlave(self, slave):  self._slave = slave

    @staticmethod
    def getInstance():  return Singleton.getInstance(AccountManager)


    def getClubByIndex(self, index):
        for cid in self._clubs:
            club = self._clubs[cid]
            if club.index == index:
                return club
        return None

    def createClub(self, args):
        """创建俱乐部
        args为字典，为创建俱乐部必须的参数
        """
        pass

    def prepare_clubs(self):
        """将所有club读入内存 status=1"""
        active_clubs = []
        err, data = gameDataInterface.getAllClub()
        #db.cur.callproc('find_active_clubs')
        #results = db.cur.fetchall()
        active_clubs = {item[0]: GameClub(uuid=item[0]) for item in results}
        # for k, v in active_clubs.items():
        #     print k, v
        return active_clubs

    def create_new_club(self, *args, **kwargs):
        """创建俱乐部 name, chair_uuid, game_types
        name:俱乐部名称　char_uuid:主席用户id"""
        result = {}
        try:
            name = kwargs.get('name', '')
            chairman = kwargs.get('chair_uuid')
            game_type = kwargs.get('game_types')
            uuid = compress_uuid()
            create_time = time.time()

            # 调用存储过程，创建一条俱乐部信息
            db.cur.callproc('create_game_club', (chairman, create_time, uuid,
                                                 name, game_type))
            # 生成club对象加载到内存中
            self._clubs['uuid'] = GameClub(uuid=uuid)
            result['status'] = 'ok'
            result['msg'] = 'create new club success'
        except GameException as game_error:
            result['status'] = 'failed'
            result['msg'] = game_error.message
            print "club init error: {}".format(game_error.message)
        except Exception as e:
            result['status'] = 'failed'
            result['msg'] = e.message
            print "club init error: {}".format(e.message)
        finally:
            return result

    def applying_for_club(self, *args, **kwargs):
        """申请加入俱乐部, 通过club_id, 申请加入俱乐部
        user_id, club_id=None, club_name=None
        """
        result = {}
        try:
            # TODO 暂由客户端确保user和club id的正确
            new_cur(db)
            club_id = kwargs.get("club_id")
            user = kwargs.get("user_id")
            appling_time = time.time()
            if not club_id:
                raise GameException("club_id or club_name is need!")
            db.cur.callproc('club_appling', (club_id, user, appling_time))

            result['status'] = 'ok'
            result['msg'] = 'apply success'
        except GameException as game_err:
            result['result'] = 'failed'
            result['msg'] = game_err.message
        except Exception as e:
            result['result'] = 'failed'
            result['msg'] = e.message
        finally:
            return result


