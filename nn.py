import numpy as np

class NeuralNetwork:
    def __init__(self,layers: list,learningRate=0.001) -> None:
        self.layersConfig = layers 
        self.learningRate = learningRate
        self.time = 0 #tracks time for ADAM
        self.createActivations()
        self.createWeights()
        self.createBiases()
        self.createVecs()

    def reLU(self,x: float) -> float: #an activation function
        return x * (x > 0)

    def reLUd(self,x: float) -> float: #lreLU derivative with respect to x
        return 1 * (x > 0)    

    def lreLU(self,x: float) -> float: #an improvement on reLU that allows for small negative values
         #return x * (x > 0) + x*0.01 * (x <= 0)
         return np.maximum(0.01*x,x) #vectorized
    
    def lreLUd(self,x: float) -> float: #lreLU derivative with respect to x
        #return 1 * (x > 0) +0.01 * (x <= 0)
        return np.where((x > 0),1,0.01) # type: ignore
    
    def normalise(self,x: float,min: float,max: float) -> float:  #not in use
        return (x-min)/(max-min)
    
    def createActivations(self) -> None:
        self.activations = [layer for layer in self.layersConfig]
        for i in range(len(self.activations)):
            self.activations[i] = np.zeros(self.activations[i])

    def createWeights(self) -> None:
        self.weights = []
        for i in range(len(self.layersConfig)-1):
            self.weights.append(np.random.randn(self.layersConfig[i+1],self.layersConfig[i]) * np.sqrt(2/self.layersConfig[i])) #create matrixes of weight connections between layers
        self.mW = [np.zeros_like(layer) for layer in self.weights] #for ADAM
        self.vW = [np.zeros_like(layer) for layer in self.weights] #for ADAM

    def createBiases(self) -> None: #can use list comprehensions when bothered for all the create funcs
        self.biases = [layer for layer in self.layersConfig] 
        for i in range(len(self.layersConfig)-1):
            self.biases[i] = np.zeros(self.layersConfig[i+1])
        self.biases = self.biases[:-1]

        self.mB = [np.zeros_like(layer) for layer in self.biases] #for ADAM
        self.vB = [np.zeros_like(layer) for layer in self.biases] #for ADAM

    def findCost(self,desired: float,actual: float) -> float: #a function to give a cost value that is then used for backpropagation
        return (actual-desired)**2

    def feedFwd(self,k: int,n: int) -> float: #n denoting the layer that calculations are being done with, k denoting the next layers node being activated 
        return np.dot(self.weights[n][k],self.activations[n]) + self.biases[n][k]
        
    def forwardPropagation(self,inputs) -> None: 
        self.activations[0] = np.array(inputs)
        self.preActivations = [layer.copy() for layer in self.activations] 
        
        for i in range(len(self.layersConfig)-1): # will activate nodes from the inputs, using the former nodes, weights and biases to activate the latter nodes, propagating until it reaches the output
            self.preActivations[i+1] = np.dot(self.weights[i],self.activations[i]) + self.biases[i] #vectorized version of the feedFwd function, the entire next layer = a vector of the dot products of the weight matrix and activation vector of the current layer + a vector of the biases of that layer.
            self.activations[i+1] = self.lreLU(self.preActivations[i+1]) #applies an activation function
        self.activations[-1] = (self.preActivations[-1]) #if its the last layer (output layer) it wont have an activation function applied after being fed forwards 

                #for j in range(len(self.activations[i+1])): #an unvectorized version to make it easier to understand
                    #self.preActivations[i+1][j] = self.feedFwd(j,i) 
                    # self.activations[i+1] = (self.preActivations[i+1])     

    def createVecs(self) -> None:
        self.errorVec = [np.zeros_like(layer) for layer in self.activations] #creates an empty nested array that has the shape of all the nodes in the network
        self.gradVecB = [np.zeros_like(layer) for layer in self.biases] #creates an empty nested array that has the shape of all the nodes in the network
        self.gradVecW = [np.zeros_like(layer) for layer in self.weights] #creates an empty nested matrix array that has the shape of all connections betweens nodes in the network

    def backPropagation(self,desiredValues: np.ndarray) -> None:
        desiredValues = np.array(desiredValues)
        self.errorVec[-1] = 2*(self.activations[-1]-desiredValues) #the cost function with respect to the activation (dcda)
        for i in range(len(self.layersConfig)-1): #find error of every neuron
            if i != 0:
                dzda = self.lreLUd(self.preActivations[-2-i]) #the preactivation value with respect to the activation function
                reverseWeights = self.weights[-1-i].T #flips/transposes the weight matrix so it can be accessed backwards
                self.errorVec[-2-i] = dzda * np.dot(reverseWeights,self.errorVec[-1-i]) #takes the whole current layer dzdas (activations) and multiplies them by a vector of the sum all the weights*error of the next layer related to each of the current neurons
            else:
                self.errorVec[-2-i] = np.dot(self.weights[-1-i].T,self.errorVec[-1-i]) #the last neuron isnt activated so it doesnt need dzda
                
            #                                   0              0          ^
            #                                   .              0          | the loop here essentially calculates these connections but for the entire current layer
            #                                   .              0
        for i in range(len(self.gradVecW)): 
            # for j in range(len(self.gradVecW[-i-1])):
            #     self.gradVecW[-1-i][j] = self.activations[-2-i]*self.errorVec[-1-i][j] 
            self.gradVecW[-1-i] = np.outer(self.errorVec[-1-i],self.activations[-2-i]) #the code commented before is a prevectorized format of this code that is easier to digest, vectorising makes it quicker though

        self.gradVecB = self.errorVec[1:] #the bias gradient vector is equivilent to the errorVector, slices the input layer biases, as they arent needed

    def standardGradientDescent(self) -> None: #although not very useful when compared to ADAM, can be used to compare optimization algorithms
        for i in range(len(self.gradVecW)):
             self.weights[i] = self.weights[i] - self.gradVecW[i]*self.learningRate

        for i in range(len(self.gradVecB)):
            self.biases[i] = self.biases[i] - self.gradVecB[i]*self.learningRate
            
    def adamGradientDescent(self) -> None: #much faster than standardGradientDescent but much more memory intensive (3x)
        beta1 = 0.9
        beta2 = 0.999
        eps = 0.0000001
        self.time += 1 #set at 0 in initilization

        a =(1-beta1**(self.time)) #Mhat bias correction
        b =(1-beta2**(self.time)) #Vhat bias correction

        for i in range(len(self.gradVecW)):
                self.mW[i] = beta1 * self.mW[i] + (1-beta1) * self.gradVecW[i]  #creates the first moment (mean average)
                self.vW[i] = beta2 * self.vW[i] + (1-beta2) * (self.gradVecW[i]**2) #creates the second moment (variance)
                mWhat = self.mW[i]/a #moment 1 bias correction
                vWhat = self.vW[i]/b  #moment 2 bias correction
                self.weights[i] = self.weights[i] - self.learningRate * mWhat/(np.sqrt(vWhat) + eps) #updates matrix


        for i in range(len(self.gradVecB)):
                self.mB[i] = beta1 * self.mB[i] + (1-beta1) * self.gradVecB[i] #same as weight but for biases
                self.vB[i] = beta2 * self.vB[i] + (1-beta2) * (self.gradVecB[i]**2)
                mBhat = self.mB[i]/a
                vBhat = self.vB[i]/b
                self.biases[i] = self.biases[i] - self.learningRate * mBhat/(np.sqrt(vBhat) + eps)

    def performAction(self,inputs: list) -> list: #calculates an output depending on the training, doesnt use the new data to learn
        self.forwardPropagation(inputs)
        return self.activations[-1]
    
    def playEpisode(self,inputs: list,desiredResults: list,display=False) -> list:# performs the action and learns from it
        self.forwardPropagation(inputs) #runs a forward pass to find costs, back pass to find gradient vectors, then applies the updates using gradient descent
        self.backPropagation(desiredResults)
        self.adamGradientDescent()
        if display: #displays the data for debugging/visualization
            print(f"epoch: {self.time} number(s): {inputs}, desired: {desiredResults}   prediction: {round(self.activations[-1][0])} cost: {round(sum(self.findCost(desiredResults,self.activations[-1])),3)}, %: {round(abs(desiredResults[0] - self.activations[-1][0]) / abs(desiredResults[0])*100,3)}") # type: ignore
        return self.activations[-1]