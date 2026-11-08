import pygame,random,copy
import algorithms as a
import numpy as np
global frame1,frame2

class Map: # Map will be a fixed size 16x16 as AI is the main purpose of the project
    global window
    def __init__(self):
        self.size = 12#16
        self.map = [["0" for i in range(self.size)] for j in range(self.size)]
        self.pallete = {"0": (10,10,10),
                        "1": (0,random.randint(99,99),0),
                        "2": "red"}

    def draw(self):
        #print("drawing")
        scale = 800/len(self.map)
        for i in range(len(self.map[0])):
            for j in range(len(self.map)):
                pygame.draw.rect(window,self.pallete[self.map[j][i]],(scale*i,scale*j,scale,scale),random.randint(12,15))


class Snake:
     global grid
     def __init__(self):
          grid.map[5][5] = "1"
          grid.map[5][4] = "1"
          grid.map[5][3] = "1"
          grid.map[5][2] = "1"
          self.body = [(5,2),(5,3),(5,4)]
          self.head = [5,5]
          self.dir = (0,1)
          self.foodpos = [8,8]
          self.foodposCopy = [8,8]
          self.foodDist = [0,0]
          self.applesEaten = 0
     def move(self,dir):
            self.body.append(self.head)  # type: ignore (TO GET RID OF VSCODE ERROR)
            self.head = [self.head[0]+dir[0],self.head[1]+dir[1]]
            if self.head[0] < 0 or self.head[0] > 15:
                print("LOSE")
                return True
            if self.head[1] < 0 or self.head[1] > 15:
                print("LOSE")
                return True
            if grid.map[self.head[0]][self.head[1]] == "2":
                pass
            else:
                grid.map[self.body[0][0]][self.body[0][1]] = "0"
                self.body = self.body[1:]
            if grid.map[self.head[0]][self.head[1]] == "1":
                print("LOSE")
                return True
            grid.map[self.head[0]][self.head[1]] = "1"

            #print(len(grid.map))

    # hasher = {"0": (-1,0), #up
    #             "1": (0,-1), #left
    #             "2": (1,0), #down
    #             "3": (0,1)} #right

     def move2(self,dir):
            reward = 0
           # print(dir,self.dir)
            if dir == (0,-1):
                #print("left")
                if self.dir == (0,1):
                    reward -=1/20
                    dir = self.dir
                    
            elif dir == (1,0):
                #print("down")
                if self.dir == (-1,0):
                    reward -=1/20
                    dir = self.dir

            elif dir == (0,1):
                #print("right")
                if self.dir == (0,-1):
                    reward -=1/20
                    dir = self.dir

            elif dir == (-1,0):
                #print("up")
                if self.dir == (1,0):
                    reward -=1/20
                    dir = self.dir
            self.dir = dir
                
            
            self.body.append(self.head) # type: ignore (TO GET RID OF VSCODE ERROR)
            self.head = [self.head[0]+dir[0],self.head[1]+dir[1]]
            
            if self.head[0] < 0 or self.head[0] > grid.size -1: #hitting walls
                #print("LOSE")
                if self.applesEaten < 2:
                    reward -=10
                reward -=10
                return grid.map,reward,True
            if self.head[1] < 0 or self.head[1] > grid.size -1:
                #print("LOSE")
                if self.applesEaten < 2:
                    reward -=10
                reward -=10
                return grid.map,reward,True

            x = (grid.size - 1) - abs(snake.foodposCopy[1] - snake.head[1])   
            y = (grid.size - 1) - abs(snake.foodposCopy[0]-snake.head[0]) 
            if (x**2 + y**2) < (self.foodDist[0]**2 + self.foodDist[1]**2):
                reward -=0
                #print("bad")
            else:
                reward +=0.
                #print("good")
            
            if grid.map[self.head[0]][self.head[1]] == "2":
                reward +=(20+self.applesEaten*2)
                self.applesEaten +=1
                #print("Nom",self.applesEaten)
            else:
                grid.map[self.body[0][0]][self.body[0][1]] = "0"
                self.body = self.body[1:]

            if grid.map[self.head[0]][self.head[1]] == "1":
                #print("LOSE")
                reward -=10
                if self.applesEaten < 2:
                    reward -=10
                grid.map[self.head[0]][self.head[1]] = "1"

                return grid.map,reward,True
            
            grid.map[self.head[0]][self.head[1]] = "1"
            reward -=0.1
            return grid.map,reward,False


     def makeFood(self):#
          count = 0
          for i in range(len(grid.map)):
            if not("2" in grid.map[i]):
                pass
            else:
                count +=1
                if count == 1: #control food count
                    return True
          while True:
            self.foodpos = [random.randint(1,len(grid.map)-2),random.randint(1,len(grid.map)-2)]
            if grid.map[self.foodpos[0]][self.foodpos[1]] == "0":
                grid.map[self.foodpos[0]][self.foodpos[1]] = "2"
                self.foodposCopy = self.foodpos.copy()
                self.foodpos[0] = int(self.foodpos[0]/grid.size) 
                self.foodpos[1] = int(self.foodpos[1]/grid.size)
                return False
   
grid = Map()
snake = Snake()
pygame.init()
res = (800,800)
window = pygame.display.set_mode(res)
clock = pygame.time.Clock()
run = True
direction = (0,1)
queue = []


# frame1 = grid.map
# frame2 = grid.map

def update():

    window.fill((0,0,0))
    grid.draw()
    snake.makeFood()
    clock.tick(10)
    #print(reward,"fo")
    pygame.display.flip()

def perform(output): #takes an output from network and performs it
    #print("performed move")
    snake.makeFood()
    hasher = {"0": (-1,0), #up
                "1": (0,-1), #left
                "2": (1,0), #down
                "3": (0,1)} #right
    decision = hasher[str(output)]
    currState = sum(grid.map,[])
    nextState,reward,isDone = snake.move2(decision)


    isCollide = [0,0,0,0]
    if snake.head[0] == 0:
        isCollide[0] = 1
    if snake.head[0] == grid.size -1:
        isCollide[1] = 1
    if snake.head[1] == 0:
        isCollide[2] = 1
    if snake.head[1] == grid.size -1:
        isCollide[3] = 1

    surroundings = [0,0,0,0]
    try:
       #if int(grid.map[snake.head[0]+1][snake.head[1]]) == "1":
        surroundings[0] = int(grid.map[snake.head[0]+1][snake.head[1]])
    except:
       surroundings[0] = 1

    try:
       surroundings[1] = int(grid.map[snake.head[0]][snake.head[1] + 1])
    except:
       surroundings[1] = 1

    try:
       surroundings[2] = int(grid.map[snake.head[0] - 1][snake.head[1]])
    except:
       surroundings[2] = 1

    try:
       surroundings[3] = int(grid.map[snake.head[0]][snake.head[1] - 1])
    except:
       surroundings[3] = 1

    # surroundings = [int(grid.map[snake.head[0] + 1][snake.head[1]]),
    #                 int(grid.map[snake.head[0]][snake.head[1] + 1]),
    #                 int(grid.map[snake.head[0] - 1][snake.head[1]]),
    #                 int(grid.map[snake.head[0]][snake.head[1] - 1])]

    #print(surroundings)
    x = (grid.size - 1) - abs(snake.foodposCopy[1] - snake.head[1])   
    y = (grid.size - 1) - abs(snake.foodposCopy[0]-snake.head[0]) 
    
    #snake.foodposCopy[0] - 1
    danger = [max(isCollide)]
    return [snake.head[0]/grid.size,snake.head[1]/grid.size] + list(snake.dir) + snake.foodpos + isCollide + surroundings + [x/(grid.size-1),y/(grid.size-1)] + danger,reward,isDone
    #return sum(nextState,[]) + snake.head + list(snake.dir) + snake.foodpos + isCollide + surroundings,reward,isDone
    #return currState+sum(nextState,[])+ snake.foodpos + isCollide,reward,isDone #returns flattened image after action is performed, reward, and done status


def empty():
    return None
done = False



# network = a.DQN([2+2+4,256,128,64,4])
network = a.DQN([2+2+2+2+4+4+1,64,32,16,8,4])
isCollide = [0,0,0,0]
surroundings = [0,0,0,0]
foodPos = [0,0]
initState = snake.head + list(snake.dir) + snake.foodpos + isCollide + surroundings + foodPos + [0]
#initState = sum(grid.map,[]) + snake.head + list(snake.dir) + snake.foodpos + isCollide + surroundings
#initState = sum(grid.map,[]) + sum(grid.map,[]) + snake.foodpos + isCollide
#initState = snake.head + snake.foodpos + isCollide


# initState = snake.head + snake.foodpos + isCollide
display = True

while run:
    #clock.tick(10) #fps
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYUP:
                # if event.key == pygame.K_w:
                #     direction = (-1,0)
                # if event.key == pygame.K_a:
                #     direction = (0,-1)
                # if event.key == pygame.K_s:
                #     direction = (1,0)
                # if event.key == pygame.K_d:
                #     direction = (0,1)
                if event.key == pygame.K_SPACE:
                    if display == False:
                        display = True
                    else:
                        display = False
                # if event.key == pygame.K_s:
                #     network.saveArrays("snek")

                # if event.key == pygame.K_l:
                #     network = network.loadArrays("snek")
                # if event.key == pygame.K_p:
                #     network.plotResults()
    #print([snake.head[0]/grid.size,snake.head[1]/grid.size],snake.dir,snake.foodpos,isCollide,surroundings,x,y)
    
    
    nextState,reward,isDone = snake.move2(direction)
    update()
    if display:
        network.playEpisode(initState,perform,update,True)
    else:
        network.playEpisode(initState,perform,empty,True)




    
    #frame2=grid.map

    print(snake.applesEaten)
    if isDone:
        grid = Map()
        snake = Snake()
        direction = (0,1)

    pygame.display.flip()

pygame.quit()

