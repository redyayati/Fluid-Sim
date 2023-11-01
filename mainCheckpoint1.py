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


class Particle():
    def __init__(self ,x , y ) : 
        self.pos = Vector2(x,y) 
        self.vel = Vector2()
        self.acc = Vector2()
        self.size = 4
        self.damping = .9
    def update(self) : 
        self.vel += self.acc * deltaT
        self.pos += self.vel * deltaT
        self.boundry()
    def show(self) : 
        col = 255,255,255,200
        # gfx.filled_circle(screen ,int(self.pos.x) , int(self.pos.y) , int(self.size) , col)
        pg.draw.circle(screen , (255,0,0) , (self.pos.x , self.pos.y) , self.size)
        pg.draw.circle(screen , (0,0,0) , (self.pos.x , self.pos.y) , self.size,1)
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
            forces[i] += NORMALIZATION_PRESSURE_FORCE * (
            -
            (
                particles[j].pos
                -
                particles[i].pos
            ) / distances[i][j_in_list]
            *
            (
                pressures[j]
                +
                pressures[i]
            ) / (2 * densities[j])
            *
            (
                sRad
                -
                distances[i][j_in_list]
            )**2
            )
    return forces
def viscousForce():
    forces = [Vector2() for i in range(len(particles))] 
    for i in range(len(particles)) :
        for j_in_list , j in enumerate(neighbors_ids[i]) : 
            if i == j or distances[i][j_in_list] == 0: continue
            forces[i] += NORMALIZATION_VISCOUS_FORCE * (
                            (
                                particles[j].vel
                                -
                                particles[i].vel
                            ) / densities[j]
                            *
                            (
                                sRad
                                -
                                distances[i][j_in_list]
                            )
                            )
    return forces
mass = 1 
sRad = 9
deltaT = .01
pressureConstant = 200
referenceDensity = 1.5
gravity = Vector2(0,7)
viscosity = .6
NORMALIZATION_DENSITY = ((315 * mass) / (64 * math.pi * sRad**9))
NORMALIZATION_PRESSURE_FORCE = (-(45 * mass) / (math.pi * sRad**6))
NORMALIZATION_VISCOUS_FORCE = ((45 * viscosity * mass) / (math.pi * sRad**6))

box = Box(100,200)
mrgn = 10
particles = []
rows = 8
cols = 8
gap =  8
createParticles()

positions = [[0,0] for i in range(len(particles))]

updatePositions()

while running : 
    screen.fill((55,55,55))
    fps_counter()    
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

    # forces = [Vector2() for i in range(len(particles))] 
    # for i in range(len(particles)) :
    #     for j_in_list , j in enumerate(neighbors_ids[i]) : 
    #         if i == j or distances[i][j_in_list] == 0: continue
    #         forces[i] += NORMALIZATION_PRESSURE_FORCE * (
    #         -
    #         (
    #             particles[j].pos
    #             -
    #             particles[i].pos
    #         ) / distances[i][j_in_list]
    #         *
    #         (
    #             pressures[j]
    #             +
    #             pressures[i]
    #         ) / (2 * densities[j])
    #         *
    #         (
    #             sRad
    #             -
    #             distances[i][j_in_list]
    #         )**2
    #         )

    #         forces[i] += NORMALIZATION_VISCOUS_FORCE * (
    #         (
    #             particles[j].vel
    #             -
    #             particles[i].vel
    #         ) / densities[j]
    #         *
    #         (
    #             sRad
    #             -
    #             distances[i][j_in_list]
    #         )
    #     )
    #     forces[i] += gravity


    pressForce = pressureForce()
    viscForce = viscousForce()
    for i in range(len(particles)) : 
        netForce = pressForce[i] + viscForce[i] + gravity
        particles[i].acc = netForce / densities[i]
        # particles[i].acc = forces[i] / densities[i]
        particles[i].update()
        
    updatePositions()

    for par in particles : par.show()
    box.showBox()

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