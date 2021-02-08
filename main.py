
import xlrd
import xlwt

def getspotdata():
    readbook = xlrd.open_workbook(r'spot.xls')
    sheet = readbook.sheet_by_index(0)#索引的方式，从0开始
    col = sheet.col_values(0)
    nrows = sheet.nrows#行
    
    print(col)
    return col,nrows

#col,nrows = getspotdata()

def getdiredata():
    readbook = xlrd.open_workbook(r'dire.xls')
    sheet = readbook.sheet_by_index(0)#索引的方式，从0开始
    col0 = sheet.col_values(0)
    col1 = sheet.col_values(1)
    col2 = sheet.col_values(2)
    nrows = sheet.nrows#行
    #print(col2)
    
    return col0,col1,col2,nrows

col0,col2,col2,nrows2 = getdiredata()

#设置初始出发地点，如 千代田区綃4
#start_spot="千代田区綃4"

#设置到达时间，如 13：30
from datetime import date
from datetime import datetime
from datetime import timedelta
#start_date = date(2018, 10, 18);
start_datetime = datetime(2021, 2, 1, 7, 30, 0)
#print(start_datetime)
end_datetime = datetime(2021,2,1,20,30,0)
#设置游玩时间， 如3天
day =  3

#设置
import MCTS
print("生成MCTS-AI管理器")
mcts_manager = MCTS.mcts(timeLimit=10000)#开启mcts程序

print("初始化中...")
initialstate=MCTS.State(nowspot="A",
                        travelpoint=0,
                        moneycost=0,
                        now_datetime=start_datetime,
                        end_datetime=end_datetime,
                        hasbeenspots=[])

print("开启MCTS-AI中...")
root = mcts_manager.search(initialState=initialstate)
print(root.children)
"""
for action in root.children:
    print(action,root.children[action])"""
    

