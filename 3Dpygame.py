import pygame
import math
import numpy as np
import sqlite3
import json

pygame.init()
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
done = False

# ---------------- DB LOAD ----------------
# Connect to the SQLite database
conn = sqlite3.connect("sprite.sqlite")
cursor = conn.cursor()

# Get the first sprite from the DB
cursor.execute("SELECT SpriteID, Edges, Vetex FROM Sprite LIMIT 1")
row = cursor.fetchone()
if row:
    sprite_id, edges_json, vetex_json = row
    print(f"Loaded sprite: {sprite_id}")

    # Parse JSON fields from DB
    vertices = [np.array(v) for v in json.loads(vetex_json)]
    # Each edge in DB is stored as JSON strings of point coordinates
    edges_raw = json.loads(edges_json)
    edges = []
    for edge_str in edges_raw:
        e = json.loads(edge_str)  # gives ["[x,y,z]", "[x,y,z]"]
        p1 = np.array(json.loads(e[0]))
        p2 = np.array(json.loads(e[1]))
        edges.append((p1, p2))
else:
    print("No sprites found in database.")
    vertices = []
    edges = []

conn.close()
# ------------------------------------------

def perspective(userPoint, objPoint, camDirection):
    forward = camDirection / np.linalg.norm(camDirection)
    right = np.array([-forward[1], forward[0], 0])
    up = np.array([0, 0, 1])
    user2obj = objPoint - userPoint

    xCam = np.dot(user2obj, right)
    yCam = np.dot(user2obj, forward)
    zCam = np.dot(user2obj, up)

    scale = 300 / yCam
    xScreen = xCam * scale + 400
    yScreen = 400 - zCam * scale

    return xScreen, yScreen

def vector2xy(point1, point2, userPoint, camDirection):
    distance1 = np.dot(camDirection, point1 - userPoint)
    distance2 = np.dot(camDirection, point2 - userPoint)

    if distance1 < 0 and distance2 < 0:
        return None, None
    elif distance1 >= 0 and distance2 >= 0:
        start = perspective(userPoint, point1, camDirection)
        end = perspective(userPoint, point2, camDirection)
        return start, end
    elif distance1 < 0:
        t = (0.1 - distance1) / (distance2 - distance1)
        point1 = point1 + t * (point2 - point1)
    else:
        t = (0.1 - distance2) / (distance1 - distance2)
        point2 = point2 + t * (point1 - point2)

    start = perspective(userPoint, point1, camDirection)
    end = perspective(userPoint, point2, camDirection)
    return start, end

def displayLine(p1, p2, pointPlane, normal, c):
    start, end = vector2xy(p1, p2, pointPlane, normal)
    try:
        pygame.draw.line(screen, c, start, end, 2)
    except:
        pass

# Camera setup
user = np.array([0, 0, 0])
viewAngle = 90

# ------------- Main Loop -------------
while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        viewAngle -= 3
    if keys[pygame.K_RIGHT]:
        viewAngle += 3
    if keys[pygame.K_UP]:
        user[1] += math.sin(math.radians(viewAngle)) * 2
        user[0] += math.cos(math.radians(viewAngle)) * 2
    if keys[pygame.K_DOWN]:
        user[1] -= math.sin(math.radians(viewAngle)) * 2
        user[0] -= math.cos(math.radians(viewAngle)) * 2

    camDirection = np.array([math.cos(math.radians(viewAngle)), math.sin(math.radians(viewAngle)), 0])
    screen.fill((255, 255, 255))

    # Draw sprite edges from DB
    for p1, p2 in edges:
        displayLine(p1, p2, user, camDirection, (0, 0, 0))

    crosshair = pygame.Rect(400, 380, 10, 10)
    pygame.draw.rect(screen, (0, 0, 0), crosshair)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()