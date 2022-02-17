import time
import random

BATTERY_MIN = 30

global blackboard





blackboard = {
    "BATTERY_LEVEL": 100,
    "SPOT_CLEANING": 1,
    "GENERAL_CLEANING": 1,
    "DUSTY_SPOT": 1,
    "HOME_PATH": 1
}

#Global variables for counts
spCount = -1
genCount = -1
timeCount = 0



class status(object):
    FAILURE = 0
    SUCCESS = 1
    RUNNING = -1

class node:
    pass


class task(node):
  def __int__(self, leaves):
    self.leaves = leaves

class condition(node):
  def __int__(self, leaves):
    self.leaves = leaves

class composite(node):
  def __init__(self, leaves):
    self.leaves = leaves

class decorator(node):
  def __int__(self, leaves):
      self.leaves = leaves



#COMPOSITES

class sequence(composite):
  def run(self):
    for i in self.leaves:
      if i.run() == status.FAILURE:
        return status.FAILURE
      elif i.run()== status.RUNNING:
        return status.RUNNING
    return status.SUCCESS


class selection(composite):
  def run(self):
    for i in self.leaves:
      if i.run() == status.RUNNING:
        return status.RUNNING
      elif i.run()== status.SUCCESS:
        return status.SUCCESS
    return status.FAILURE


class priority(composite):
  def run(self):
    for i in self.leaves:
      if i.run() == status.RUNNING:
        return status.RUNNING
      elif i.run()== status.SUCCESS:
        return status.SUCCESS
    return status.FAILURE



#TASKS
class batteryCheck(condition):
  def run(self):
    if blackboard["BATTERY_LEVEL"] < BATTERY_MIN:
      print ("BATTERY_LEVEL: ", blackboard["BATTERY_LEVEL"], "% TOO LOW")
      print ("Please charge")
      return status.SUCCESS
    else:
      return status.FAILURE


class spotCheck(condition):
  def run(self):
    if blackboard["SPOT_CLEANING"] == 1:
      return status.SUCCESS
    else:
      return status.FAILURE


class dustySpotCheck(condition):
  def run(self):
    if (genCount == -1):
      found = random.randint(0,20)
      if found != 0:
        print ("DUSTY_SPOT -- FOUND")
        blackboard["DUSTY_SPOT"] = 1
        blackboard["DUSTY_SPOT"] = 0
      else:
        blackboard["DUSTY_SPOT"] = 0
    if blackboard["DUSTY_SPOT"] == 1:
      return status.SUCCESS
    else:
      return status.FAILURE


class checkGeneral(condition):
  def run(self):
    if blackboard["GENERAL_CLEANING"] == 1:
      return status.SUCCESS
    else:
      return status.FAILURE





class cleanSpot(task):
  def __init__(self, cycle):
    self.cycle = cycle
  def run(self):
    if (spCount> 0):
      print("SPOT CLEANING, ON CYCLE #", spCount)
      count -= 1
      time.sleep(1)
      timeCount += 1
      blackboard["BATTERY_LEVEL"] -= 1
      return status.RUNNING
    if spCount == 0:
      return status.SUCCESS
    if spCount == -1:
      count = self
    


class findHome(task):
  def run(self):
    global timeCount
    print("findHome -- RUNNING")
    time.sleep(1)
    timeCount += 1
    return status.SUCCESS
   
  


class goHome(task):
  def run(self):
    global timeCount
    print("goHome -- RUNNING")
    time.sleep(1)
    timeCount += 1
    return status.SUCCESS


class dock(task):
  def run(self):
    print("DOCKING -- RUNNING")
    return status.SUCCESS


class spotDone(task):
  def run(self):
    blackboard["SPOT_CLEANING"] = 0
    print("SPOT_CLEANING -- DONE")
    return status.SUCCESS


class done_general(task):
  def run(self):
    blackboard["GENERAL_CLEANING"] = 0
    print("GENERAL_CLEANING -- DONE")
    return status.SUCCESS

#1 battery level for cleaning
class cleanFloor(task):
  def run(self):
    global timeCount
    print("cleanFloor - RUNNING")
    time.sleep(1)
    timeCount += 1
    blackboard["BATTERY_LEVEL"] -= 1
    random_done = random.randint(0, 20)
    if random_done == 10:
      print("THE house if clean!")
      return status.FAILURE
    return status.RUNNING


class doNothing(task):
  def run(self):
    global timeCount
    print("Dothing--RUNNING")
    time.sleep(1)
    timeCount += 1
    return status.SUCCESS


class generalClean(task):
  def __init__(self, cycle):
    self.cycle = cycle
  def run(self):
    global timeCount
    if (genCount > 0):
      print("RUNNING GENERAL_SPOT_CLEANING ON CYCLE #", genCount)
      genCount -= 1
      time.sleep(1)
      timeCount += 1
      blackboard["BATTERY_LEVEL"] -= 1
      return status.RUNNING
    if genCount == -1:
      genCount = self.cycle
    if genCount == 0:
      blackboard["DUSTY_SPOT"] = 0
      return status.SUCCESS
   

#DECORATOR
class isFailed(decorator):
  def __init__(self, leaves):
    self.leaves = leaves
  def run(self):
    if self.leaves.run() == status.FAILURE:
      return status.SUCCESS
    else:
      return status.RUNNING

# build behavior tree
bTree = priority(leaves = [
                   sequence(leaves = [
                              batteryCheck(),
                              findHome(),
                              goHome(),
                              dock()]),
                   selection(leaves = [
                              sequence(leaves = [
                                          spotCheck(),
                                          cleanSpot(20),
                                          spotDone()]),
                              sequence(leaves = [
                                          checkGeneral(),
                                                    sequence(leaves =
                                                            [priority(leaves =
                                                                      [sequence(leaves = [
                                                                                   dustySpotCheck(),
                                                                                   generalClean(35)]),
                                                                       isFailed(cleanFloor())
                                                                      ]),
                                                            done_general()
                                                            ]),
                                                   ]),

                               ]),
                   doNothing()
                ])


def main():
  #TO TEST PLEASE SUBSTITUE VALUES HERE 
  #PUT 1 (in general or spot cleaning) IF THAT IS THE SELECTED COMMAND, 0 SIGNIFIES THAT YOU DO NOT WANT SOMETHING TO BE EXECUTED
  blackboard["BATTERY_LEVEL"] = 40
  blackboard["SPOT_CLEANING"] = 1
  blackboard["GENERAL_CLEANING"] = 0

  success = bTree.run()
  while (success != 1 or blackboard["SPOT_CLEANING"] == 1 or blackboard["GENERAL_CLEANING"] == 1):
    success = bTree.run()
    global timeCount
    if blackboard["BATTERY_LEVEL"] < BATTERY_MIN:
      success = bTree.run()
      print(" PROGRAM RUNNING")
      print("########### BLACKBOARD VALUES ###########")
      print(blackboard)
      print("#########################################")
      print("")
      print("CHARGING")
      time.sleep(5)
      timeCount += 5
      blackboard["BATTERY_LEVEL"] = 100
      print("CHARGING COMPLETED, BATTERY_LEVEL: ", blackboard["BATTERY_LEVEL"], "%")
      #print("*******************start running **********************")
  if (success == 1):
    print("Tasks are done!")
    print("It took: ", timeCount, " seconds")
    
       
if __name__ == "__main__":
    main(

)
