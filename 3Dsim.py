import pygame
import math 
import numpy as np
pygame.init()
screen = pygame.display.set_mode((800,400))
done = False #establishing initial state to run pygame
clock = pygame.time.Clock()

def perspective(userPoint, objPoint, camDirection):
    forward = camDirection / np.linalg.norm(camDirection) #unit vector of camera direction
    right = np.array([-forward[1], forward[0], 0]) #gets the rightward direction based on the camera
    up = np.array([0, 0, 1]) #assumes upward direction is along the z-axis

    user2obj = objPoint - userPoint #vector from user to object

    #uses scalar dot product to find how far the object is in each camera-relative direction
    xCam = np.dot(user2obj, right)
    yCam = np.dot(user2obj, forward)
    zCam = np.dot(user2obj, up)

    scale = 300 / yCam #scales things based on depth to simulate perspective
    xScreen = xCam * scale + 400 #translates x to screen coordinates, centered at 400
    yScreen = 400 - zCam * scale #inverts y so positive is up on screen

    return xScreen, yScreen

def vector2xy(point1, point2, userPoint, camDirection):
    #finds how far each point is from the camera plane
    distance1 = np.dot(camDirection, point1 - userPoint)
    distance2 = np.dot(camDirection, point2 - userPoint)

    #skips drawing if both points are behind the camera
    if distance1 < 0 and distance2 < 0:
        return None, None
    elif distance1 >= 0 and distance2 >= 0: #if both are in front
        start = perspective(userPoint, point1, camDirection)
        end = perspective(userPoint, point2, camDirection)
        return start, end
    elif distance1 < 0:
        #clips the first point so it's just in front of the camera
        t = (0.1 - distance1) / (distance2 - distance1)
        point1 = point1 + t * (point2 - point1)
    else:
        #clips the second point so it's just in front of the camera
        t = (0.1 - distance2) / (distance1 - distance2)
        point2 = point2 + t * (point1 - point2)

    start = perspective(userPoint, point1, camDirection)
    end = perspective(userPoint, point2, camDirection)
    return start, end

def displayLine(p1, p2, pointPlane, normal, c):
    start, end = vector2xy(p1, p2, pointPlane, normal)

    try:
        pygame.draw.line(screen, c, start, end, 2) #draws a 2-pixel wide line between screen coordinates
    except:
        pass #skips if points aren't valid

#------object and camera setup----------
user = np.array([0, 0, 0])
viewAngle = 90

#defines the 3d corners of a cube
square = [
    np.array([0, 45, 0]),
    np.array([0, 40, 0]),
    np.array([30, 40, 0]),
    np.array([30, 45, 0]),
    np.array([0, 45, 5]),
    np.array([0, 40, 5]),
    np.array([30, 40, 5]),
    np.array([30, 45, 5])
]

#face definitions (not used yet, for future solid rendering maybe)
faces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 4, 7, 3),
    (1, 5, 6, 2),
    (0, 1, 5, 4),
    (3, 2, 6, 7)
]

#edges that define how the cube's corners connect
squareEdges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]

#base corners of a pyramid
pyramidBase = [
    np.array([35, 40, 0]),
    np.array([45, 40, 0]),
    np.array([45, 50, 0]),
    np.array([35, 50, 0])
]

#the tip of the pyramid
pyramidTop = np.array([40, 45, 10])

#combines base and tip
pyramid = pyramidBase + [pyramidTop]

#defines which points to connect with lines
pyramidEdges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (0, 4), (1, 4), (2, 4), (3, 4)
]

#------main loop----------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    #------controls-------
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]: viewAngle -= 3 #rotates camera left
    if keys[pygame.K_RIGHT]: viewAngle += 3 #rotates camera right
    if keys[pygame.K_UP]: 
        user[1] += (math.sin(math.radians(viewAngle)) * 2) #moves forward in y
        user[0] += (math.cos(math.radians(viewAngle)) * 2) #moves forward in x
    if keys[pygame.K_DOWN]: 
        user[1] -= (math.sin(math.radians(viewAngle)) * 2) #moves backward in y
        user[0] -= (math.cos(math.radians(viewAngle)) * 2) #moves backward in x

    camDirection = np.array([math.cos(math.radians(viewAngle)), math.sin(math.radians(viewAngle)), 0]) #camera direction from view angle
    screen.fill((255, 255, 255)) #clears the screen to white

    #------draw wireframes-------
    for e in squareEdges:
        displayLine(square[e[0]], square[e[1]], user, camDirection, (0, 0, 0)) #draws cube lines

    for e in pyramidEdges:
        displayLine(pyramid[e[0]], pyramid[e[1]], user, camDirection, (200, 0, 0)) #draws pyramid lines

    crosshare = pygame.Rect(400, 380, 10, 10) #creates a small target rectangle
    pygame.draw.rect(screen, (0, 0, 0), crosshare) #draws the target on screen
    pygame.display.flip() #refreshes the screen to show the new frame
    clock.tick(60) #limits the game to 60 fps

pygame.quit()
