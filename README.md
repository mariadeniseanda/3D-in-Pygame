# 3D-in-Pygame

This is a program that renders a 3D environment in Pygame. I’m fully aware that I’m not the first and won’t be the last to do this. However, I decided to take on this task to challenge my problem-solving, programming, and math skills. I deliberately coded this using only my existing knowledge (first-year engineering-level math and programming), and I limited my use of external help. So I’m sure there are much more streamlined ways to write this. That said, I still think it may be helpful for people around my skill level. In this README file, I’ll go into detail on how the program works.  
<br>

### What You Will Need

You’ll need to have _pygame_ and the _numpy_ libraries installed on your device. Also, make sure your version of Python includes the standard _math_ library (any recent version should be fine).

---

### The Foundation

This program works by “placing” the user in a 3D coordinate space, with the X-Y plane as the “floor” and the Z-axis representing the “up and down” direction. Every object in this space has an X, Y, Z coordinate — including the user. The user starts at the origin:

```python
user = np.array([0, 0, 0])  # np is numpy
```

You can move around the X-Y plane using the _Up_ and _Down_ keys. The _Right_ and _Left_ keys rotate your view — this changes your viewing angle with respect to the X-axis. That angle determines your viewing direction. Simple trigonometry is used to calculate this direction vector:

```python
np.array([math.cos(math.radians(viewAngle)), math.sin(math.radians(viewAngle)), 0])
```

---

### Objects

Objects in this space are made out of points (vertices) stored as a list of _numpy_ vectors:

```python
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
```

Each element in this list represents a single 3D point: `[X, Y, Z]`. Together, they form the eight corners of a rectangular prism — basically a stretched cube.

- The first four points (indices 0–3) form the bottom face of the shape.
- The last four (indices 4–7) form the top face, which is elevated along the Z-axis by 5 units.

To connect these vertices into faces or edges:

```python
# Optional face definitions — not used yet, maybe for future solid rendering
faces = [
    (0, 1, 2, 3),
    (4, 5, 6, 7),
    (0, 4, 7, 3),
    (1, 5, 6, 2),
    (0, 1, 5, 4),
    (3, 2, 6, 7)
]

# Edges — define how the cube’s corners connect
squareEdges = [
    (0, 1), (1, 2), (2, 3), (3, 0),
    (4, 5), (5, 6), (6, 7), (7, 4),
    (0, 4), (1, 5), (2, 6), (3, 7)
]
```

---

### The *perspective* Function

This function figures out where an object is, relative to the user’s position and viewing direction.

First, it calculates the camera's forward direction. Since we only care about direction (not distance), the unit vector is used:

```python
forward = camDirection / np.linalg.norm(camDirection)
```

Then, the "right" direction is calculated by rotating the forward vector 90° in the X-Y plane:

```python
right = np.array([-forward[1], forward[0], 0]) 
```

Next, the "up" direction is set. Since the camera can’t tilt up or down, this always points along the Z-axis:

```python
up = np.array([0, 0, 1])
```

Now we figure out where the object is, relative to the user:

```python
user2obj = objectPoint - userPoint
```

Then we project that vector onto the camera axes using dot products. This gives us how far the object is in the right, forward, and up directions:

```python
xCam = np.dot(user2obj, right)
yCam = np.dot(user2obj, forward)
zCam = np.dot(user2obj, up)
```

Perspective is simulated by scaling things based on how far forward they are (`yCam`). Objects further away get drawn smaller:

```python
scale = 300 / yCam
xScreen = xCam * scale + 400
yScreen = 400 - zCam * scale
```

---

### Converting Points into Edges

The function `_displayline_` handles drawing a line between two 3D points — but only if they’re visible.

Before drawing, it checks how far each point is from the camera plane:

```python
distance1 = np.dot(camDirection, point1 - userPoint)
distance2 = np.dot(camDirection, point2 - userPoint)
```

If **both** points are behind the camera, nothing is drawn:

```python
if distance1 < 0 and distance2 < 0:
    return None, None
```

If **both** are in front, we pass them to the `perspective` function to get their screen positions:

```python
elif distance1 >= 0 and distance2 >= 0:
    start = perspective(userPoint, point1, camDirection)
    end = perspective(userPoint, point2, camDirection)
    return start, end
```

If **only one** point is behind, it gets clipped — meaning we calculate where the line intersects the camera plane and shift that point forward just slightly. This avoids visual glitches and infinite scale issues.

```python
elif distance1 < 0:
    t = (0.1 - distance1) / (distance2 - distance1)
    point1 = point1 + t * (point2 - point1)
else:
    t = (0.1 - distance2) / (distance1 - distance2)
    point2 = point2 + t * (point1 - point2)
```

Once both points are in front of the camera, we can project and return them as screen coordinates:

```python
start = perspective(userPoint, point1, camDirection)
end = perspective(userPoint, point2, camDirection)
return start, end
```


## EDITS!!
I have started working on a backend to make sprites easier! I decided to use node.js so I can learn js in the process. It is still in the working stages but I thought I'd share!
