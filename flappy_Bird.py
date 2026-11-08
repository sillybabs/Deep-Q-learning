import pygame,random
import DQlearning as a 




pygame.init()
res = (1300,800)
window = pygame.display.set_mode(res)

run = True


class bird:
     def __init__(self):
          self.pos = [200,400]
          self.g = 9.8
          self.acceleration = 0
          self.body = pygame.Rect(self.pos[0],500-self.pos[1],40,20)
          self.score = 0

     def jump(self):
          t=2
          self.acceleration = (-4.20/t)*5
          self.pos[1]+=(10/t)*5
          
     def draw(self):
          self.body = pygame.Rect(self.pos[0],500-self.pos[1],40,20)
          #pygame.draw.rect(window,"yellow",self.body)

          
          self.picture  = pygame.image.load("bird.png")
          self.picture = pygame.transform.scale(self.picture,(50,25))
          self.rotation = -self.acceleration*3
          self.picture2 = pygame.transform.rotate(self.picture,self.rotation)



          window.blit(self.picture2,(self.pos[0]-5,500-self.pos[1] -5))
     def applyPhysics(self):
          if self.pos[1] > 500: #roof
               self.pos[1] = 500
               self.acceleration = 0
               return -5
          
          if self.pos[1] > 52: 
            self.pos[1] -=self.acceleration

          else: #floor
            #self.acceleration = 0
            return -5
          self.acceleration +=0.1*8
          return 0
     
     def checkCollision(self,other):
          if self.body.colliderect(other):
               return True
          else:
               return False

class tubes:
     def __init__(self):
          self.pos = [1300,0]
          self.hole = random.randint(50,300)
          self.holeSize= 200
          self.len1 = self.hole 
          self.len2 = 500-self.hole-self.holeSize
          self.tube1 =pygame.Rect(self.pos[0],500-self.len1-self.pos[1],80,self.len1)
          self.tube2 =pygame.Rect(self.pos[0],self.pos[1],80,self.len2)

     def draw(self):
          self.len1 = self.hole 
          self.len2 = 500-self.hole-self.holeSize
          self.tube1 =pygame.Rect(self.pos[0],500-self.len1-self.pos[1],80,self.len1)
          self.tube2 =pygame.Rect(self.pos[0],self.pos[1],80,self.len2)

          self.picture  = pygame.image.load("Tube1.png")
          self.picture = pygame.transform.scale(self.picture,(80,self.len1))
          window.blit(self.picture,(self.pos[0],500-self.len1-self.pos[1]))

          self.picture  = pygame.image.load("Tube2.png")
          try:
               self.picture = pygame.transform.scale(self.picture,(80,self.len2))
               window.blit(self.picture,(self.pos[0],self.pos[1]))
          except:
               pygame.draw.rect(window,"green",self.tube2)
          #pygame.draw.rect(window,"red",self.tube1)
          #pygame.draw.rect(window,"green",self.tube2)

     def move(self):
          self.pos[0] -=4*5
          if self.pos[0] < 0-80:
               return True
          else:
               return False



flap = bird()
tube = tubes()
clock = pygame.time.Clock()
isDone = False

def logic():
    global flap,tube
    reward = 0
    reward = flap.applyPhysics()

    if flap.checkCollision(tube.tube1) or flap.checkCollision(tube.tube2):
         reward -=10
         return reward,True

    if tube.pos[0] == 200:
         flap.score +=1
         reward +=10
         print("POINT",flap.score)
    
    if flap.pos[1] > tube.len1-tube.pos[1] and flap.pos[1] < tube.hole+tube.holeSize:

         reward +=0.5
    else:
         reward -=0.1
    
    mid = (tube.hole+tube.holeSize + tube.len1-tube.pos[1])/2
    reward -= abs(mid-flap.pos[1])/400
    #print(abs(mid-flap.pos[1])/400)
    if tube.move(): #if the tube has passed
         tube = tubes()

    reward +=0.1
    return reward,False

def update():
    #clock.tick(30)
    # window.fill("blue")
    picture  = pygame.image.load("bgFlap.jpg")
    picture = pygame.transform.scale(picture,(window.get_size()[0],500))

    window.blit(picture,(0,0))
    flap.draw()
    tube.draw()
    pygame.display.flip()

def perform(move):
     global flap,tube
     flap.draw()
     tube.draw()
     if move == 0:
          flap.jump()
     else:
          pass
     reward,isDone = logic()
     if ((tube.hole+tube.holeSize + tube.len1-tube.pos[1])/2) > flap.pos[1]:
          above = 1
     else:
          above = 0
     state =   [flap.pos[1]/500]  + [flap.acceleration/4.20] + [above] + [((tube.hole+tube.holeSize + tube.len1-tube.pos[1])/2)/500] + [abs((flap.pos[0]-tube.pos[0]))/500] + [(tube.len1-tube.pos[1])/500] + [(tube.hole+tube.holeSize)/500]
     return state,reward,isDone


#bird pos, tube pos, velocity
def empty():
    return None
update()
display = True
initState = [flap.pos[1]/500]  + [flap.acceleration/4.20] + [1] + [((tube.hole+tube.holeSize + tube.len1-tube.pos[1])/2)/500] + [(abs(flap.pos[0]-tube.pos[0]))/500] + [(tube.len1-tube.pos[1])/500] + [(tube.hole+tube.holeSize)/500]

network = a.DQN([1+1+1+1+1+1+1,16,16,2])


while run:
    #print([((tube.hole+tube.holeSize + tube.len1-tube.pos[1])/2)/500],[(tube.len1-tube.pos[1])/500])
    update()
    
    a,isDone = logic()
    if display:
        network.playEpisode(initState,perform,update)
    else:
         network.playEpisode(initState,perform,empty)
    for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    flap.jump()
                if event.key == pygame.K_s:
                    network.saveArrays("flap")
                if event.key == pygame.K_l:
                    network = network.loadArrays("flap")
                if event.key == pygame.K_p:
                    network.plotResults()
                if event.key == pygame.K_SPACE:
                    if display == False:
                        display = True
                    else:
                        display = False
    #print([flap.pos[1]/500] , [flap.acceleration/4.20] , [(tube.len1-tube.pos[1])/500] , [(tube.hole+tube.holeSize)/500])
    pygame.display.flip()
    clock.tick(10)
    if isDone:

     flap = bird()
     tube = tubes()  
     isDone = False
    update()


pygame.quit()

