# coding: utf-8

from CommonProtocol import *
from GeneralPack import GeneralPack




try:
    from gameCfg import GameCfg 
    exec "from %s import *" % GameCfg.gameProtocol
except:
    print "no module name gameCfg"
