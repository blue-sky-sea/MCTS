from __future__ import division
import copy 
import time
import math
import random
import xlrd
from datetime import date
from datetime import datetime
from datetime import timedelta
print("READ IN DATA...")
readbook = xlrd.open_workbook(r'dire.xls')
sheet = readbook.sheet_by_index(0)#索引的方式，从0开始
global TRAFFIC_ORIGINAL_LIST
global TRAFFIC_DESTINATION_LIST
global TRAFFIC_COSTTIME_LIST
global TRAFFIC_COSTMONEY_LIST
global TRAFFIC_POINT_LIST
TRAFFIC_ORIGINAL_LIST = sheet.col_values(0)
TRAFFIC_DESTINATION_LIST = sheet.col_values(1)
TRAFFIC_COSTTIME_LIST = sheet.col_values(2)#时间
TRAFFIC_COSTMONEY_LIST = sheet.col_values(3)#钱
TRAFFIC_POINT_LIST = sheet.col_values(4)#satr

readbook = xlrd.open_workbook(r'spot.xls')
sheet = readbook.sheet_by_index(0)#索引的方式，从0开始
global SPOT_NAME_LIST
global SPOT_LOCATION_LIST
global SPOT_COSTTIME_LIST
global SPOT_POINT_LIST
global SPOT_COSTMONEY_LIST
SPOT_NAME_LIST = sheet.col_values(0)
SPOT_LOCATION_LIST = sheet.col_values(1)
SPOT_COSTTIME_LIST = sheet.col_values(2)#时间
SPOT_POINT_LIST = sheet.col_values(3)
SPOT_COSTMONEY_LIST= sheet.col_values(4)#钱
print("READ IN DATA SUCCESS!")



class State():
    def __init__(self,
                 nowspot,
                 travelpoint,
                 moneycost,
                 now_datetime,
                 end_datetime,
                 hasbeenspots):
        self.nowspot = nowspot
        self.travelpoint = travelpoint
        self.moneycost = moneycost  #已经花费的钱
        self.now_datetime = now_datetime #当前的日期和时间点
        self.end_datetime = end_datetime #结束旅行的时间
        self.hasbeenspots = hasbeenspots #当前状态下已经去过的兴趣点
    def takeSecond(self,elem):
        return elem[1]      
    def getgoodspot(self,nowspotname,n):
        
        global TRAFFIC_ORIGINAL_LIST
        global TRAFFIC_DESTINATION_LIST
        global TRAFFIC_COSTTIME_LIST
        global TRAFFIC_COSTMONEY_LIST
        global TRAFFIC_POINT_LIST
        possible_spots = []
        flag= False
        
        #score = point/time
        for i in range(len(TRAFFIC_ORIGINAL_LIST)):
            if(str(TRAFFIC_ORIGINAL_LIST[i]) == str(nowspotname)):
                flag=True
                #hasbeenspot
                if(TRAFFIC_DESTINATION_LIST[i] not in self.hasbeenspots):
                    #input("spotsname2[i] is not in hasbeenspot")
                    score = float(float(TRAFFIC_POINT_LIST[i])/TRAFFIC_COSTTIME_LIST[i])
                    item = (i,score)#下标+score
                    possible_spots.append(item)
                else:
                    pass
                    #print(spotsname2[i],hasbeenspot)
                    #input("spotsname2 is in hasbeenspot")
            if(TRAFFIC_ORIGINAL_LIST[i]!= str(nowspotname) and flag==True):
                break 
            
        #排序取前n个
        possible_spots.sort(key=self.takeSecond)
        #(i,3.6/40) i2 is score
        return possible_spots[:n]
    
    def getPossibleActions(self):
        n=5
        #print("【getPossibleAction】:nowspot",self.nowspot)
        possible_good_spots = self.getgoodspot(self.nowspot,n)
        return possible_good_spots
    
    #判断当前是否该结束旅程了
    def isTerminal(self):
        #now_datetime=datetime(2021, 2, 1, 13, 30, 0)
        s = (self.end_datetime-self.now_datetime).total_seconds()
        #print("[isTerminal]:",s)
        #input()
        if(s/60 <= 60*3):
            return True,self.travelpoint
        #print("[isTerminal]:","False")
        return False,self.travelpoint
    
    def getReward(self):
        #TODO
        #根据当前的用户评价value、综合游览时长、已经花费的钱结合计算reward（奖励计算公式如何获得是需要考虑的）
        isTerminal,flag = self.isTerminal()
        #print("getReward-flag:",flag)
        return flag
    def getspotdata(self,name):
        global SPOT_NAME_LIST
        global SPOT_LOCATION_LIST
        global SPOT_COSTTIME_LIST
        global SPOT_POINT_LIST
        global SPOT_COSTMONEY_LIST
        ite = 0
        for i in range(len(SPOT_NAME_LIST)):
            if(SPOT_NAME_LIST[i]==name):
                ite=i
                break
        #print("【getspotdata】",SPOT_COSTTIME_LIST[ite],SPOT_POINT_LIST[ite],SPOT_COSTMONEY_LIST[ite])
        
        return SPOT_COSTTIME_LIST[ite],SPOT_POINT_LIST[ite],SPOT_COSTMONEY_LIST[ite]
    def takeAction(self,actionlist):
        global TRAFFIC_ORIGINAL_LIST
        global TRAFFIC_DESTINATION_LIST
        global TRAFFIC_COSTTIME_LIST
        global TRAFFIC_COSTMONEY_LIST
        global TRAFFIC_POINT_LIST

        i=actionlist[0]
        spotcosttime,spotpoint,spotcostmoney = self.getspotdata(TRAFFIC_DESTINATION_LIST[i])
        action1 = Action(original = TRAFFIC_ORIGINAL_LIST[i],
                         destination = TRAFFIC_DESTINATION_LIST[i],
                         traffic_time = TRAFFIC_COSTTIME_LIST[i],
                         traffic_point = float(TRAFFIC_POINT_LIST[i]),
                         traffic_cost = TRAFFIC_COSTMONEY_LIST[i],
                         destination_time = spotcosttime,
                         destination_point = spotpoint,
                         destination_cost = spotcostmoney)
        
        print("[takeAction]:",TRAFFIC_ORIGINAL_LIST[i],"->",TRAFFIC_DESTINATION_LIST[i],
              " traffictime:",TRAFFIC_COSTMONEY_LIST[i]," destinationtime:",spotcosttime)
        newstate = copy.deepcopy(self)
        if(self.nowspot == action1.original):
            newstate.nowspot = action1.destination
            newstate.moneycost = int(newstate.moneycost)+int(action1.traffic_cost)+int(action1.destination_cost)  #已经花费的钱
            newstate.now_datetime= newstate.now_datetime +timedelta(minutes=action1.traffic_time)+timedelta(minutes=action1.destination_time) #当前的日期和时间点
            
            #TODO
            #最麻烦的就是value如何计算比较好
            star_line=3.5
            star_bonus=0.5
            if(float(action1.traffic_point)>=star_line):
                traffic_value = (action1.traffic_point-star_line+star_bonus)*500/((action1.traffic_time+5)*(action1.traffic_cost+10))    
            else:
                traffic_value = (star_line-action1.traffic_point)*((action1.traffic_time+5)*(action1.traffic_cost)+10)/1000
            
            star_line=3.6
            star_bonus=0.4
            if(float(action1.destination_point)>=star_line):
                destination_value = (action1.destination_point-star_line+star_bonus)*500/((action1.destination_time+5)*(action1.destination_cost+10))    
            else:
                destination_value = (star_line-action1.destination_point)*((action1.destination_time+5)*(action1.destination_cost+10))/1000
            hasbeen_spot_num = len(self.hasbeenspots)
            newstate.travelpoint = (self.travelpoint + traffic_value + destination_value)/(len(newstate.hasbeenspots))
            newstate.hasbeenspots.append(newstate.nowspot)
        else:
            print("takeAction:wrong")
            return None
        return newstate
    
class Action():
    def __init__(self,original,destination,
                 traffic_time,traffic_point,traffic_cost,
                 destination_time,destination_point,destination_cost):
        self.original = original #出发地点
        self.destination = destination #到达地点
        
        self.traffic_time = traffic_time #交通花费的时间
        self.traffic_point = traffic_point #交通的评分
        self.traffic_cost = traffic_cost #路途所需花费的钱
        
        self.destination_time = destination_time #到达地点后游览所需要花费的时间
        self.destination_point = destination_point #地点的评分       
        self.destination_cost = destination_cost #兴趣点所需花费的钱
        
def randomPolicy(state):
    print("RANDOMPOLICY:spot:",state.nowspot,state.travelpoint)
    while not state.isTerminal():
        try:
            action = random.choice(state.getPossibleActions())
        except IndexError:
            raise Exception("Non-terminal state has no possible actions: " + str(state))
        state = state.takeAction(action)
    #print()
    return state.getReward()


class treeNode():
    def __init__(self, state, parent):
        self.state = state
        #self.isTerminal = state.isTerminal()
        self.isTerminal,flag= state.isTerminal() #代表当前的状态是否是终结态
        self.isFullyExpanded = self.isTerminal #节点是否完全扩展
        #self.isFullyExpanded = self.isTerminal
        self.parent = parent
        self.numVisits = 0
        self.totalReward = 0#多次采样后获得的travelpoint总和
        #TODO实际应该用一个参数表示平均旅行体验
        self.children = {}

    def __str__(self):
        s=[]
        s.append("totalReward: %s"%(self.totalReward))
        s.append("numVisits: %d"%(self.numVisits))
        s.append("isTerminal: %s"%(self.isTerminal))
        s.append("possibleActions: %s"%(self.children.keys()))
        return "%s: {%s}"%(self.__class__.__name__, ', '.join(s))

class mcts():
    def __init__(self, timeLimit=None, iterationLimit=None, explorationConstant=1 / math.sqrt(2),
                 rolloutPolicy=randomPolicy):
        if timeLimit != None:
            if iterationLimit != None:
                raise ValueError("Cannot have both a time limit and an iteration limit")
            # time taken for each MCTS search in milliseconds
            self.timeLimit = timeLimit
            self.limitType = 'time'
        else:
            if iterationLimit == None:
                raise ValueError("Must have either a time limit or an iteration limit")
            # number of iterations of the search
            if iterationLimit < 1:
                raise ValueError("Iteration limit must be greater than one")
            self.searchLimit = iterationLimit
            self.limitType = 'iterations'
        self.explorationConstant = explorationConstant
        self.rollout = rolloutPolicy

    def search(self, initialState, needDetails=False):
        #mizukiyuta||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki
        print("创建root结点,初始地点为：",initialState.nowspot," 出发时间：",initialState.now_datetime," 结束时间：",initialState.end_datetime)
        initialState.hasbeenspots.append(initialState.nowspot)
        #mizukiyuta||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki||mizukimizuki
        
        self.root = treeNode(initialState, None)

        if self.limitType == 'time':
            timeLimit = time.time() + self.timeLimit / 1000
            while time.time() < timeLimit:
                self.executeRound()
        else:
            for i in range(self.searchLimit):
                self.executeRound()
        
        
        #self.getBestRoute(self.root)
        return self.root
    
        """
        bestChild = self.getBestChild(self.root, 0)
        action=(action for action, node in self.root.children.items() if node is bestChild).__next__()
        if needDetails:
            return {"action": action, "expectedReward": bestChild.totalReward / bestChild.numVisits}
        else:
            return action"""

    def executeRound(self):
        """
            execute a selection-expansion-simulation-backpropagation round
        """
        node = self.selectNode(self.root)
        reward = self.rollout(node.state)
        self.backpropogate(node, reward)

    def selectNode(self, node):
        while not node.isTerminal:
            if node.isFullyExpanded:
                node = self.getBestChild(node, self.explorationConstant)
            else:
                return self.expand(node)
        return node

    def expand(self, node):
        actions = node.state.getPossibleActions()
        for action in actions:
            if action not in node.children:
                newNode = treeNode(node.state.takeAction(action), node)
                node.children[action] = newNode
                if len(actions) == len(node.children):
                    node.isFullyExpanded = True
                return newNode

        #raise Exception("Should never reach here")

    def backpropogate(self, node, reward):
        while node is not None:
            node.numVisits += 1
            node.totalReward += reward
            node = node.parent

    def getBestChild(self, node, explorationValue):
        bestValue = float("-inf")
        bestNodes = []
        for child in node.children.values():
            nodeValue = child.totalReward / child.numVisits + explorationValue * math.sqrt(
                2 * math.log(node.numVisits) / child.numVisits)
            if nodeValue > bestValue:
                bestValue = nodeValue
                bestNodes = [child]
            elif nodeValue == bestValue:
                bestNodes.append(child)
        return random.choice(bestNodes)
    def getBestRoute(self,root):
        nownode = root
        print(len(nownode.children))
        
        while(True):
            #input("round")
            if(len(nownode.children)>0):
                bestChild = self.getBestChild(nownode, 0) 
                action1 = None
                #node1 = None
                for action, node in self.root.children.items():
                    if node is bestChild:
                        action1 = action
                        print(action1,"%"*10)
                        nownode = node
                    else:
                        print("not best",action)
            else:
                print("break")
                break