
import nn
import numpy as np
import random,copy
import pickle

class DQN: #Q-rious george
    def __init__(self,netConfig: list): #first in the config is the parameter length, and last is the amount of actions and activations are Q values
        self.OnlineNet = nn.NeuralNetwork(netConfig,0.001)
        self.TargetNet = nn.NeuralNetwork(netConfig,0.001)
        self.gamma = 0.99 #discount
        self.epsilon = 1.0
        self.epsDecay = 0.995
        self.bufferCap = 10000
        self.learningBuffer = 500
        self.expBuff = [[] for i in range(self.bufferCap)] #creates a queue
        self.expBuffSample = [i for i in range(len(self.expBuff))]
        self.updateFreq = 100
        self.batchSize = 64
        self.episodeIncr = 1
        self.expIncr = 0
        self.totalReward = 0
        self.totalLoops = 0
        self.autosave = False
        self.maxReward = 0
        self.xArray = []
        self.yArray = []
        self.expBuffWeights = [0 for i in range(len(self.expBuff))]

    def saveArrays(self,name: str) -> None:
        if name == "auto":
            name = self.saveName
        else:
            self.saveName = name
        with open(f'{name}.pkl', 'wb') as f:
            pickle.dump(self, f)
        
        self.autosave = True
        print("autosave on")

    
    def loadArrays(self,name: str) -> None:
        print("loaded",self.totalReward)
        self.autosave = True
        with open(f'{name}.pkl', 'rb') as f:
            return pickle.load(f)


    def copyMain(self) -> None:
        self.TargetNet.weights = copy.deepcopy(self.OnlineNet.weights)
        self.TargetNet.biases = copy.deepcopy(self.OnlineNet.biases)


    def TDE(self,reward: float) -> float:
        return (reward + self.gamma*self.TargetNet.activations[-1][np.argmax(self.OnlineNet.activations[-1])])
    
    def mask(self,value: float,pos: int) -> np.ndarray:
        maskedArray = np.zeros_like(self.OnlineNet.activations[-1])
        maskedArray[pos] = value
        return maskedArray
    
    def epsilonGreedy(self) -> None: #True is exploitation, False is exploration
        if np.random.randint(1,101) > self.epsilon*100:
            #choose best
            self.action = np.argmax(self.OnlineNet.activations[-1]) #argmax returns the index
        else:
            #choose random
            self.action = random.randint(0,len(self.OnlineNet.activations[-1])-1)
        #if Eps at 0.01 or less, keep so theres still a chance at exploration
        

    def learnExperience(self,experience: list,num: int) -> None: # SARSD [State, Action, Reward, Next State,Done]

        self.OnlineNet.forwardPropagation(experience[0])    
        currentQ = self.OnlineNet.activations[-1].copy()
        if experience[4]:
            targets = experience[2]  #mask transforms single value to vector
        else:
            self.OnlineNet.forwardPropagation(experience[3]) 
            self.TargetNet.forwardPropagation(experience[3])
            targets = self.TDE(experience[2]) #bellman
        self.OnlineNet.forwardPropagation(experience[0]) 
        currentQ[experience[1]] = targets - currentQ[experience[1]]
        self.expBuffWeights[num] = abs(currentQ[experience[1]])
        self.OnlineNet.backPropagation(currentQ)
        self.OnlineNet.adamGradientDescent()


    def findTDerror(self,experience: list) -> None: # SARSD [State, Action, Reward, Next State,Done]
        self.OnlineNet.forwardPropagation(experience[0])    
        currentQ = self.OnlineNet.activations[-1][experience[1]].copy()
        if experience[4]:
            targets = experience[2]  
        else:
            self.OnlineNet.forwardPropagation(experience[3]) 
            self.TargetNet.forwardPropagation(experience[3])
            targets = self.TDE(experience[2]) #bellman
        self.OnlineNet.forwardPropagation(experience[0]) 
        currentQ = targets - currentQ
        TDerror = currentQ
        self.expBuffWeights[self.expIncr%self.bufferCap] = abs(TDerror)


    def addToBuffer(self,experience: list) -> None:
        self.expBuff[self.expIncr%self.bufferCap] = experience #creates a cyclical queue <--- mention this
        self.expIncr +=1 


        
    def ExperienceBuffer(self) -> None: # SARSD [State, Action, Reward, Next State,Done]
            for i in range(self.batchSize):
                choice = random.choices(self.expBuffSample,self.expBuffWeights)[0]
                self.learnExperience(self.expBuff[choice],choice)

         

    def updateState(self,func) -> None:
        func()


    def plotResults(self) -> None:
        import matplotlib.pyplot as plt
        plt.plot(self.xArray,self.yArray)
        plt.show()


    def playEpisode(self,initState: list,perform,stateUpdate,convert=True) -> None: #the state being the input such as an image of the game  
        done = False
        self.totalLoops +=1
        print(self.totalLoops)
        if self.totalLoops%10 == 0 and self.autosave and self.totalReward/100 > self.maxReward:
            self.saveArrays("auto")
            print("SAVED",self.maxReward)
            self.maxReward = self.totalReward/100

 
        if self.totalLoops%100 == 0:
            self.yArray.append(self.totalReward/100)
            self.xArray.append(self.totalLoops)
            print(f"learning {self.totalReward/100,self.epsilon,self.totalLoops,self.episodeIncr}")
            self.totalReward = 0





        
        if self.epsilon > 0.01:
            self.epsilon = self.epsilon*self.epsDecay 
        while not(done):
            if convert:
                initState = list(map(int,initState))
            self.OnlineNet.forwardPropagation(initState)
            self.TargetNet.forwardPropagation(initState)

            #select action from online net
            self.epsilonGreedy()

            #execute
            nextState,reward,done = perform(self.action)
            if done:
                pass
            if convert:
                nextState = list(map(int,nextState))
            self.action = int(self.action)
            self.totalReward += reward


            finish = stateUpdate() # used in games file to update state visually on the display

            #store the transition (all the steps) for the experience buffer
            experience = [initState,self.action,reward,nextState,done] #SARSD
            self.findTDerror(experience)
            self.addToBuffer(experience)

            #if the buffer has enough experiences, then start allowing it to reccolect past experiences by randomly sampling a batch
            if self.expIncr > self.learningBuffer: ##### 
                    for i in range(1):
                        self.ExperienceBuffer()
                        
            #find target values  USING THE TARGET NET, temporal difference is using the frozen net to calc targets not main so the targets dont change after every iteration
            self.episodeIncr +=1
            initState = nextState #the endstate becomes initialState 
        if self.totalLoops%self.updateFreq == 0:
            self.copyMain()
            print("COPIED MAIN")


