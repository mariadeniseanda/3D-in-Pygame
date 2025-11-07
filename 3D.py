import pygame
import math
import numpy as np
import sqlite3
import json

pygame.init()
pygame.key.set_repeat(1, 50)
screen = pygame.display.set_mode((800, 400))
clock = pygame.time.Clock()
done = False

# ---------------- DB LOAD ----------------
conn = sqlite3.connect("sprite.sqlite")
cursor = conn.cursor()

cursor.execute("SELECT SpriteID, Edges, Vetex FROM Sprite")
rows = cursor.fetchall()

sprites = {}

if rows:
    for sprite_id, edges_json, vertex_json in rows:
        vertices = [np.array(v) for v in json.loads(vertex_json)]
        edges_raw = json.loads(edges_json)

        edges = []
        for edge_str in edges_raw:
            e = json.loads(edge_str)
            p1 = np.array(json.loads(e[0]))
            p2 = np.array(json.loads(e[1]))
            edges.append((p1, p2))

        sprites[sprite_id] = {"vertices": vertices, "edges": edges}
        print(f"Loaded sprite: {sprite_id}")
else:
    print("No sprites found in database.")

conn.close()

# ------------------------------------------

def perspective(obj, user, cam):
    # Directions relative to the user
    forward = cam / np.linalg.norm(cam)
    right = np.array([-forward[1], forward[0], 0])
    up = np.array([0, 0, 1])
    user2obj = obj - user

    xCam = np.dot(user2obj, right)
    yCam = np.dot(user2obj, forward)
    zCam = np.dot(user2obj, up)

    # Avoid division by very small values
    if yCam < 0.1:
        yCam = 0.1

    scale = 300 / yCam
    xScreen = (xCam * scale) + 400
    yScreen = 400 - (zCam * scale)

    return (xScreen, yScreen)

def vector2xy(p1, p2, userPoint, camDirection):
    near_plane = 0.1
    d1 = np.dot(camDirection, p1 - userPoint)
    d2 = np.dot(camDirection, p2 - userPoint)

    # Both behind camera → skip
    if d1 < near_plane and d2 < near_plane:
        return None, None

    # Clip the line to the near plane
    if d1 < near_plane:
        t = (near_plane - d1) / (d2 - d1)
        p1 = p1 + t * (p2 - p1)
    elif d2 < near_plane:
        t = (near_plane - d2) / (d1 - d2)
        p2 = p2 + t * (p1 - p2)

    start = perspective(p1, userPoint, camDirection)
    end = perspective(p2, userPoint, camDirection)
    return start, end

def displayLine(p1, p2, user, cam, c):
    start, end = vector2xy(p1, p2, user, cam)
    if start and end:
        pygame.draw.line(screen, c, start, end, 2)

# Camera setup
user = np.array([0.0, 0.0, 0.0])
viewAngle = 90.0

# ------------- Main Loop ------------- 
while not done:
    dt = clock.tick(60) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    keys = pygame.key.get_pressed()
    move_speed = 100 * dt
    rot_speed = 100 * dt

    if keys[pygame.K_LEFT]:
        viewAngle -= rot_speed
    if keys[pygame.K_RIGHT]:
        viewAngle += rot_speed
    if keys[pygame.K_UP]:
        user[0] += math.cos(math.radians(viewAngle)) * move_speed
        user[1] += math.sin(math.radians(viewAngle)) * move_speed
    if keys[pygame.K_DOWN]:
        user[0] -= math.cos(math.radians(viewAngle)) * move_speed
        user[1] -= math.sin(math.radians(viewAngle)) * move_speed

    camDirection = np.array([
        math.cos(math.radians(viewAngle)),
        math.sin(math.radians(viewAngle)),
        0
    ])

    screen.fill((255, 255, 255))

    for sprite_id, data in sprites.items():
        for p1, p2 in data["edges"]:
            displayLine(p1, p2, user, camDirection, (0, 0, 0))

    pygame.display.flip()

pygame.quit()
