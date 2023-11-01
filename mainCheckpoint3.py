# Implemented with gravity
import random
import pygame.gfxdraw as gfx
import pygame as pg 
from pygame.math import Vector2
import math
from sklearn import neighbors
import numpy as np
pg.init()
width = 800
height = 500

screen = pg.display.set_mode((width, height))
pg.display.set_caption('Title')
clock = pg.time.Clock() 
running  = True
font = pg.font.SysFont("Arial" , 18 , bold = True)
def fps_counter():
    fps = str(round(clock.get_fps()))
    fps_t = font.render(fps , 1, pg.Color("RED"))
    screen.blit(fps_t,(10,0))
def scale(val , startX , endX , startY , endY) : 
    x1 , y1 = startX , startY
    x2 , y2 = endX , endY
    return y2 - (y2-y1)*(x2-val)/(x2-x1)
def color(value , range) : 
    hue = min(255, scale(value , 0 , range , 0,255))
    r = hue
    b = 255 - hue
    g = 255 - abs(r-b)
    return [r , g , b]
class Box():
    def __init__(self , w , h): 
        self.h =  h
        self.w = w 
        self.top = (height - h)/2
        self.bot = height - (height - h)/2
        self.right = width - (width - w)/2
        self.left = (width - w)/2
    def showBox(self) : 
        pg.draw.rect(screen , (150,255,0) , pg.Rect(self.left , self.top ,self.w, self.h+2) , 2)
class Slider() : 
    def __init__(self , x , y , w , h , val) : 
        self.x = x
        self.y = y 
        self.w = w 
        self.h = h 
        self.val = val/100
        self.thick = 10
        self.col_bar = 255,0,0,100
        self.col_rect = 255,255,255,100
        self.show()
    def showSlider(self) : 
        button = pg.mouse.get_pressed()
        if button[0] != 0 : 
            pos = pg.mouse.get_pos()
            xPos = pos[0]
            yPos = pos[1]
            if xPos > self.x and xPos < self.x + self.w and yPos > self.y and yPos < self.y + self.h: 
                self.val = (xPos - self.x) / self.w
        self.show()
    def show(self) : 
        gfx.filled_polygon(screen, ((self.x + self.val*self.w,self.y), (self.x + self.val*self.w + self.thick,self.y),(self.x + self.val*self.w + self.thick,self.y+self.h),(self.x + self.val*self.w,self.y+self.h)), self.col_bar)
        gfx.polygon(screen, ((self.x,self.y), (self.x+self.w + self.thick , self.y),(self.x+self.w + self.thick , self.y+self.h),(self.x , self.y+self.h)), self.col_rect)

class Particle():
    def __init__(self ,x , y ) : 
        self.pos = Vector2(x,y) 
        self.vel = Vector2()
        self.acc = Vector2()
        self.size = 2
        self.damping = .9
        self.col = [250,250,250]
    def update(self) : 
        self.vel += self.acc * deltaT
        self.pos += self.vel * deltaT
        self.boundry()
    def show(self) : 
        pg.draw.circle(screen , self.col , (self.pos.x , self.pos.y) , self.size)
        # pg.draw.circle(screen , (0,0,0) , (self.pos.x , self.pos.y) , self.size,1)
    def boundry(self) : 
        if self.pos.y > box.bot - self.size : 
                self.vel.y *= -1 * self.damping
                self.pos.y = box.bot - self.size 
        if self.pos.y < box.top + self.size : 
            self.vel.y *= -1 * self.damping
            self.pos.y = box.top + self.size 
        if self.pos.x > box.right - self.size : 
            self.vel.x *= -1 * self.damping
            self.pos.x = box.right - self.size 
        if self.pos.x < box.left + self.size : 
            self.vel.x *= -1 * self.damping
            self.pos.x = box.left + self.size 
def createParticles() : 
    startC = width/2 - (cols-1)*gap/2
    startR = height/2 - (rows-1)*gap/2
    for row in range(rows) :  
        for col in range(cols) :
            p = Particle(startC+col*gap , startR + row*gap)
            mrgn = 10
            # p = Particle(random.randint(box.left+mrgn,box.right-mrgn) , random.randint(box.top+mrgn, box.bot-mrgn))
            particles.append(p)
def resetParticles(): 
    startC = width/2 - (cols-1)*gap/2
    startR = height/2 - (rows-1)*gap/2
    for row in range(rows) :  
        for col in range(cols) :
            index = col + row*cols
            particles[index].pos.x =  startC+col*gap #+ random.uniform(-2,2)
            particles[index].pos.y =  startR+row*gap #+ random.uniform(-2,2)
            particles[index].vel =Vector2()
    # for p in particles : p.pos = Vector2(random.randint(box.left+mrgn,box.right-mrgn) , random.randint(box.top+mrgn, box.bot-mrgn))
    updatePositions()
def updatePositions():
    for i in range(len(particles)) : positions[i] = [particles[i].pos.x , particles[i].pos.y]
def getNeighbors():
    return neighbors.KDTree(positions,).query_radius(positions, sRad , return_distance= True , sort_results=True)
def pressureForce(): 
    forces = [Vector2() for i in range(len(particles))]
    for i in range(len(particles)) :
        for j_in_list , j in enumerate(neighbors_ids[i]) : 
            if i == j or distances[i][j_in_list] == 0: continue
            forces[i] += NORMALIZATION_PRESSURE_FORCE * (-(particles[j].pos-particles[i].pos) / distances[i][j_in_list]*(pressures[j]+pressures[i]) / (2 * densities[j])*(sRad-distances[i][j_in_list])**2)
    return forces
def viscousForce():
    forces = [Vector2() for i in range(len(particles))] 
    for i in range(len(particles)) :
        for j_in_list , j in enumerate(neighbors_ids[i]) : 
            if i == j or distances[i][j_in_list] == 0: continue
            forces[i] += NORMALIZATION_VISCOUS_FORCE * ((particles[j].vel-particles[i].vel) / densities[j]*(sRad-distances[i][j_in_list]))
    return forces
def interactionForce(inputPos , radius , strength , particleIndex): 
    epsilon = 2.220446049250313e-16
    interactionForce = Vector2()
    offset = inputPos - particles[particleIndex].pos
    sqrDst = offset.magnitude_squared()
    if sqrDst < radius*radius : 
        dst = offset.magnitude()
        if dst > 0 : dirToInput = offset / dst 
        else : dirToInput = Vector2()
        centreT = 1 - dst/radius
        interactionForce += (dirToInput *strength - particles[particleIndex].vel) * centreT 
    return interactionForce
def externalForce(particleIndex): 
    gravity = Vector2(0,700)
    if strength != 0 : 
        interactionForce = Vector2()
        offset = inputPos - particles[particleIndex].pos
        sqrDst = offset.magnitude_squared()
        if sqrDst < interactiveForceRadius*interactiveForceRadius : 
            dst = offset.magnitude()
            if dst > 0 : dirToInput = offset / dst 
            else : dirToInput = Vector2()
            centreT = 1 - dst/interactiveForceRadius
            interactionForce += (dirToInput *strength - particles[particleIndex].vel) * centreT 
            return interactionForce
    return gravity
mass = 1 
mass = 1 
sRad = 10
deltaT = .01
pressureConstant = 300
referenceDensity = 1.5
gravity = Vector2(0,20)
viscosity = .5
interactiveForceRadius = 30
forceStrength = 7000
NORMALIZATION_DENSITY = ((315 * mass) / (64 * math.pi * sRad**9))
NORMALIZATION_PRESSURE_FORCE = (-(45 * mass) / (math.pi * sRad**6))
NORMALIZATION_VISCOUS_FORCE = ((45 * viscosity * mass) / (math.pi * sRad**6))

slider1  = Slider(width-250,5,150,15 , 20)
slider2  = Slider(width-250,25,150,15 , 5)

box = Box(270,200)
mrgn = 10
particles = []
rows = 15
cols = 15
gap =  7
createParticles()

positions = [[0,0] for i in range(len(particles))]

updatePositions()
strength = 0
while running : 
    screen.fill((0,0,0))
    fps_counter()    
    # referenceDensity = 2*slider1.val + 1
    # forceStrength = 100*slider1.val * 200
    # size = 10*slider2.val + 2
    # viscosity = slider2.val + 1
    neighbors_ids , distances = getNeighbors()

    densities = [0 for i in  range(len(particles))]
    
    for i in range(len(positions)):
        for j_in_list, j in enumerate(neighbors_ids[i]):
            densities[i] += NORMALIZATION_DENSITY * (
                sRad**2
                -
                distances[i][j_in_list]**2
            )**3
    
    pressures = []
    for i in range(len(particles)) : 
        pressures.append(pressureConstant * (densities[i] - referenceDensity))

    pressForce = pressureForce()
    viscForce = viscousForce()
    if pg.mouse.get_pressed()[0] : strength = -forceStrength
    elif pg.mouse.get_pressed()[2] : strength = forceStrength
    else : strength = 0
    mx , my = pg.mouse.get_pos()
    inputPos = Vector2(mx , my)
    for i in range(len(particles)) : 
        netForce = pressForce[i] + viscForce[i]  #+ gravity
        particles[i].acc = netForce / densities[i] + externalForce(i)
        particles[i].update()
        # particles[i].size = size
        particles[i].col = color(particles[i].vel.length() , 800)
        
    updatePositions()
    for par in particles : par.show()
    pg.draw.circle(screen , (250,250,250) , (mx,my) , interactiveForceRadius , 1)
    box.showBox()
    slider1.showSlider()
    slider2.showSlider()

    for event in pg.event.get() : 
        if event.type == pg.QUIT : 
            running = False 
        elif event.type == pg.KEYDOWN : 
            if event.key == pg.K_ESCAPE : 
                running = False 
            if event.key == pg.K_r : 
                resetParticles()
    pg.display.flip()
    clock.tick(60)
pg.quit()