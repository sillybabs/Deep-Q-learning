import pygame,math,pickle
import numpy as np
import algorithms as A
pygame.init()
window = pygame.display.set_mode((1300,700),pygame.RESIZABLE)

aliveMult = 1
class Car:
    def __init__(self,position) -> None:
        self.velocity = 1.
        self.start = position.copy()
        self.acceleration = 1.
        self.cap = 15
        self.position = position
        self.bearing = np.array([[0],[-30],[1]])
        self.collision = False
        self.collision2 = False
        self.moveQueue = [0,0,0,0,0]
        self.bl = np.array([[-5],[-8],[1]])
        self.tl = np.array([[-5],[+8],[1]])
        self.tr = np.array([[+5],[+8],[1]])
        self.br = np.array([[+5],[-8],[1]])
        self.tlPos = [self.position[0] +self.tl[0][0],self.position[1] +self.tl[1][0]]
        self.trPos = [self.position[0] +self.tr[0][0],self.position[1] +self.tr[1][0]]
        self.blPos = [self.position[0] +self.bl[0][0],self.position[1] +self.bl[1][0]]
        self.brPos = [self.position[0] +self.br[0][0],self.position[1] +self.br[1][0]]


    def loadPos(self):
        self.tlPos = [self.position[0] +self.tl[0][0],self.position[1] +self.tl[1][0]]
        self.trPos = [self.position[0] +self.tr[0][0],self.position[1] +self.tr[1][0]]
        self.blPos = [self.position[0] +self.bl[0][0],self.position[1] +self.bl[1][0]]
        self.brPos = [self.position[0] +self.br[0][0],self.position[1] +self.br[1][0]]

    def draw(self):

        self.tlPos = [self.position[0] +self.tl[0][0],self.position[1] +self.tl[1][0]]
        self.trPos = [self.position[0] +self.tr[0][0],self.position[1] +self.tr[1][0]]
        self.blPos = [self.position[0] +self.bl[0][0],self.position[1] +self.bl[1][0]]
        self.brPos = [self.position[0] +self.br[0][0],self.position[1] +self.br[1][0]]
        pygame.draw.aaline(window,"red",self.tlPos,self.blPos)
        pygame.draw.aaline(window,"red",self.trPos,self.brPos)
        pygame.draw.aaline(window,"red",self.blPos,self.brPos)
        pygame.draw.aaline(window,"red",self.tlPos,self.trPos)
        
        pygame.draw.circle(window,"white",self.blPos,4)
        pygame.draw.circle(window,"white",self.brPos,4)
        pygame.draw.circle(window,"black",self.blPos,2)
        pygame.draw.circle(window,"black",self.brPos,2)

        pygame.draw.aaline(window,"green",self.position,[(self.position[0] +self.bearing[0][0]),self.position[1] +self.bearing[1][0]])
        
     

    def rotation(self,degree,forCar=True): # uses a homogeneous matrix system to allow for a rotation matrix about the player and not the origin
        degree = degree * (math.pi/180) * 0.4
        self.rotMat = np.array([[math.cos(degree),math.sin(degree),0]   #misleading as its actually read left to right 
                             ,[-math.sin(degree),math.cos(degree),0],
                              [0,0,1]])
        if forCar:
            if player.acceleration > 1.001:
                player.acceleration -=0.002


            self.tl = np.matmul(self.rotMat, self.tl)
            self.tr = np.matmul(self.rotMat, self.tr)
            self.bl = np.matmul(self.rotMat, self.bl)
            self.br = np.matmul(self.rotMat, self.br)
            self.bearing = np.matmul(self.rotMat, self.bearing)
        else:
            return np.matmul(self.rotMat, self.bearing)



    def move(self,x=1.,y=1.): # controls movement of player and player collision with walls
        self.lastMove = self.position.copy()
        mult = 0.01*self.acceleration
        dy = self.bearing[1][0]
        dx = self.bearing[0][0]
        x,y = x*dx*mult ,y*dy*mult
        self.position[0] +=-x
        self.position[1] +=y
        self.lastVec = [x,y]

    def Move(self,dir=1):
        if self.collision == False and self.collision2 == False:
            self.lastMove = self.position.copy()
        mult = 0.01*self.acceleration*dir
        dy = self.bearing[1][0]
        dx = self.bearing[0][0]
        x,y = 0.1*dx*mult ,0.1*dy*mult
        self.position[0] +=x *self.velocity
        self.position[1] +=y *self.velocity
        if self.velocity > 0:
            self.velocity -= 0.01
        if self.velocity < 0.01:
            self.velocity = 0
        reward = (self.velocity+0.001)/10
        global aliveMult,isDone


        if (self.position[0]> 1300 or self.position[0] < 0) or (self.position[1]> 700 or self.position[1] < 0):
            aliveMult = 1.2
            isDone = True
            
            car = Car(self.start)
        else:
            car = self
        return reward,car
    def accel(self,rate):
        
        if self.velocity > self.cap:
            pass
        else:
            self.velocity +=rate


    def chooseMove(self,decision):
        reward = 0
        if decision == "sprint":
            speed = 30
            self.accel(speed)
            self.cap = 250
            reward +=1
        else:
            self.cap = 50
            speed = 20
            
        if decision == "w":
            self.accel(speed)
            reward +=1

        elif decision == "s":
            self.move(speed*8,-speed*8)
            self.accel(-speed)

        elif decision == "d":
            if not(self.collision) and not(self.collision2) :
                self.rotation(-20.0)

        elif decision == "a":
            if not(self.collision)and not(self.collision2):
                self.rotation(20.0)
        return reward
class track:
    def __init__(self) -> None:
        with open(f'track.pkl', 'rb') as f: #reads the binary
            self.course = pickle.load(f)


    # def collision(self,car):
    #     global aliveMult
    #     corners = [car.blPos,car.brPos,car.tlPos,car.trPos]
    #     isDone = False
    #     for i in range(2): #iterates through all the lines
    #         firstPos = self.course[i][0]
    #         for pos in self.course[i]:
    #             nextPos = pos
    #             if (nextPos[0] == firstPos[0]):
    #                 continue
    #             else:
    #                 m = (nextPos[1] - firstPos[1]) / (nextPos[0] - firstPos[0])  # gradient of line
    #                 c = nextPos[1] - m*nextPos[0] # y intercept
    #                 for i,xy in enumerate(corners):
    #                     if abs(xy[1] - ( m*xy[0] + c)) < 2 and max(nextPos[0],firstPos[0]) >= xy[0] and min(nextPos[0],firstPos[0]) <= xy[0] and max(nextPos[1],firstPos[1]) >= xy[1] and min(nextPos[1],firstPos[1]) <= xy[1] : #if corner in the equation of the line and in the domain/range
    #                         print("deATH",random.randint(1,233))
                                                      
    #                     else:
    #                         pass
    #             firstPos = pos

    #     return car,isDone


    def castRay(self,car,amount):
        intersectionPoints = []
        adjustedBearing = car.rotation(amount,False)
        
        for i in range(2): #iterates through all the lines
            firstPos = self.course[i][0]
            intersection = [0,0]
            for pos in self.course[i]:
                nextPos = pos
                if (nextPos[0] == firstPos[0]):
                    continue
                else:
                    m1 = (nextPos[1] - firstPos[1]) / (nextPos[0] - firstPos[0])  # gradient of line
                    c1 = nextPos[1] - m1*nextPos[0] # y intercept
                m2= (adjustedBearing[1][0]/ adjustedBearing[0][0])
                c2 = car.position[1] - m2*car.position[0] 
                xNew = (c2 - c1)/(m1-m2)
                yNew = m1*xNew + c1
                for i in range(1):
                    xss= i + xNew
                    if (xss < firstPos[0] and xss > nextPos[0]) and (xss,m1*xss + c1 < firstPos[1] and xss,m1*xss + c1 > nextPos[1]):
                        intersection = [xNew,  yNew] 

                        quad = self.catergoriseIntersection(car,intersection)
                        intersectionPoints.append([intersection,quad])
                    elif (xss > firstPos[0] and xss < nextPos[0]) and (xss,m1*xss + c1 > firstPos[1] and xss,m1*xss + c1 < nextPos[1]):
                        intersection = [xNew,  yNew] 
                        quad = self.catergoriseIntersection(car,intersection)
                        intersectionPoints.append([intersection,quad])
                
                firstPos = nextPos
        point1 = [(501,505),2]
        point2 = [(500,500),4]
        pointDist = 0
        minDist1 = 1000000 #abitarily large number
        minDist2 = 1000000 #abitarily large number

        for point in intersectionPoints: #plots the closest points infront and behind it    
            v = np.array(point[0]) - np.array(car.position)
            vDot = np.dot(v,car.bearing[:2])
            if vDot < 0 and abs(vDot) < minDist1:
                minDist1 = abs(vDot)
                point1 = point
            elif vDot > 0 and vDot < minDist2:
                minDist2 = abs(vDot)
                point2 = point    
            else:
                pass 
        pygame.draw.circle(window,"red",(point1[0]),4)
        pygame.draw.circle(window,"green",(point2[0]),4)
        v1 = np.array(point1[0]) - np.array(car.position)
        v2 = np.array(point2[0]) - np.array(car.position)
        v2Dot= np.dot(v2,car.bearing[:2])
        v1Dot = np.dot(v1,car.bearing[:2])

        return [self.getDist(point1[0],car.position[:2]), self.getDist(point2[0],car.position[:2])] #the distance back and forwards (respectively)


    def castRays(self,car,amount,increment): #[1] is fwd [0] is back
        global aliveMult
        isDone = False
        fwdDists = []
        OriginDistances = course.castRay(car,0)
        fwdDists.append(float(OriginDistances[1])/100)
        fwdDists.append(float(OriginDistances[1])/100)
        if float(OriginDistances[1]) < 10:
                    aliveMult = 1.5
                    isDone = True
                    car = Car(car.start)
        for i in range(1,int(amount/2)+1):
            xDist1 = course.castRay(car,increment*i)
            xDist2 = course.castRay(car,increment*-i)
            fwdDists.append(float(xDist1[1])/100)
            fwdDists.append(float(xDist2[1])/100)
        return fwdDists,car,isDone


    def getDist(self,point1,point2):
        yCorrect = window.get_size()[1] #Y axis goes upside down in pygame so this is to fix it
        point1 = point1[:2] #gets rid of quad signature
        return (((point1[1])-(point2[1]))**2 + (point1[0]-point2[0])**2)**0.5
    
    def catergoriseIntersection(self,car,intersection):
        if intersection[1] - car.position[1] > 0 and intersection[0] - car.position[0] > 0:
            return "fwd" #quadrant the point has intersected in (4th)
        elif intersection[1] - car.position[1] < 0 and intersection[0] - car.position[0] < 0:                                                                                                   
            return "back" #quadrant the point has intersected in (2th)
        elif intersection[1] - car.position[1] > 0 and intersection[0] - car.position[0] < 0: 
            return "fwd" #quadrant the point has intersected in (3rd)
        elif intersection[1] - car.position[1] < 0 and intersection[0] - car.position[0] > 0:  
            return "back" #quadrant the point has intersected in (1st)
        
        
    def gates(self):
        pass

    def draw(self):
        for i in range(2): #draws the inside ring then the outside ring, as data is stored with interior ring index 0
            firstPos = self.course[i][0]
            for pos in self.course[i]:
                nextPos = pos
                pygame.draw.line(window,(100,100+128*i,100),firstPos,nextPos,1)
                firstPos = pos

run = True

def update():
    window.fill("black")
    pygame.draw.rect(window,"white",(0,0,1300,500),4)
    course.castRays(player,2,30)
    player.draw()
    course.draw()
    pygame.display.flip()

player = Car([100,300])
course = track()
initState = [[player.velocity],[447,133, 218, 228]]
initState = sum(initState,[])
network = A.DQN([1+4,64,64,4])

def empty():
    window.fill("black")
    player.loadPos()
    pygame.display.flip()
    return None

def perform(output): #takes an output from network and performs it
    global aliveMult
    reward = 0
    global player,course
    hasher = {"0": "w", #up
              "1": "sprint",
                "2": "a", #left
                "3": "d"} #down
    if aliveMult < 100:
        aliveMult +=  0.5 
    decision = hasher[str(output)]
    reward += player.chooseMove(decision)
    rays,player,isDone = course.castRays(player,2,30)

    nextState = [[player.velocity/100],rays]
    nextState = sum(nextState,[])

    reward2,player = player.Move()
    reward += reward2

    if isDone:
        reward -=50



    return nextState,reward+aliveMult,isDone
w,a,s,d,up,left,right,down,sprint = False,False,False,False,False,False,False,False,False




display = True
clock = pygame.time.Clock()
while run:

    if display:
        network.playEpisode(initState,perform,update,True)
    else:
        print("alt")
        network.playEpisode(initState,perform,empty,True)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYUP:

            if event.key == pygame.K_n:
                network.saveArrays("car")

            if event.key == pygame.K_m:
                network = network.loadArrays("car") #once done make network = load arrays
                
            if event.key == pygame.K_p:
                network.plotResults()

            if event.key == pygame.K_t:
                if display:
                    display = False
                else:
                    display = True
    pygame.display.flip()
pygame.quit()



    



