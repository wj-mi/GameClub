# coding:utf-8

"""
玩家举例的计算
目前根据经纬度计算
"""

import math as Math

def CalcMil(X1, Y1, X2, Y2):
    PI = 3.1415926535898
    EARTH_RADIUS = 6378137  #地球半径 

    CurRadLong = 0;    #两点经纬度的弧度
    CurRadLat = 0;
    PreRadLong = 0;
    PreRadLat = 0;
    a = 0
    b = 0;      #经纬度弧度差
    MilValue = 0;

    #将经纬度换算成弧度
    CurRadLong = (float)(X1);
    CurRadLong = CurRadLong * PI / 180.0;

    PreRadLong = (float)(X2);
    PreRadLong = PreRadLong * PI / 180.0;

    CurRadLat = (float)(Y1);
    CurRadLat = CurRadLat * PI / 180.0;

    PreRadLat = (float)(Y2);
    PreRadLat = PreRadLat * PI / 180.0;

    #计算经纬度差值
    if (CurRadLat > PreRadLat):
        a = CurRadLat - PreRadLat;
    else:
        a = PreRadLat - CurRadLat;
    if (CurRadLong > PreRadLong):
        b = CurRadLong - PreRadLong;
    else:
        b = PreRadLong - CurRadLong;
    MilValue = 2 * Math.asin(Math.sqrt(Math.sin(a / 2.0) * Math.sin(a / 2.0) + Math.cos(CurRadLat) * Math.cos(PreRadLat) * Math.sin(b / 2.0) * Math.sin(b / 2.0)));
    MilValue = (float)(EARTH_RADIUS * MilValue);
    return MilValue;


#
if __name__ == "__main__":
    print CalcMil(100,100,200,200)