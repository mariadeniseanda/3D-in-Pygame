const express = require("express");
const path = require("path");
const sqlite3 = require("sqlite3").verbose();
const ejs = require("ejs");

const app = express();
const port = 6769;

// Middleware & views
app.use(express.urlencoded({ extended: true }));
app.engine("html", ejs.renderFile);
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "../3Dpygame/views"));

// Database setup
const db = new sqlite3.Database("sprite.sqlite", (err) => {
  if (err) {
    console.error("Error opening database:", err.message);
  } else {
    console.log("Connected to SQLite database");
  }
});

db.run(`
  CREATE TABLE IF NOT EXISTS Sprite (
    SpriteID TEXT NOT NULL UNIQUE PRIMARY KEY,
    Edges TEXT DEFAULT '[]',
    Vetex TEXT DEFAULT '[]'
  )
`);

// Temporary sprite state
let newSprite = "";
let newEdges = [];
let newVetex = {};
let tempPoint = {};

// Helper: get sorted layer keys as numbers
const getSortedLayers = () => Object.keys(newVetex).map(Number).sort((a, b) => a - b);

// Routes
app.get("/", (req, res) => {
  const error = req.query.error || " ";
  db.all("SELECT SpriteID FROM Sprite", [], (err, rows) => {
    if (err) {
      console.error(err.message);
      return res.status(500).send("Database error");
    }
    res.render("home.html", { sprites: rows.map(r => r.SpriteID), error });
  });
});

app.post("/createnew", (req, res) => {
  const spriteName = req.body.spritename;
  if (!spriteName) {
    return res.redirect(`/?error=${encodeURIComponent("Sprite name is required")}`);
  }

  db.all("SELECT SpriteID FROM Sprite", [], (err, rows) => {
    if (err) {
      console.error(err.message);
      return res.status(500).send("Database error");
    }
    const existingNames = rows.map(r => r.SpriteID);
    if (existingNames.includes(spriteName)) {
      return res.redirect(`/?error=${encodeURIComponent("This sprite name already exists")}`);
    }
    newSprite = spriteName;
    res.redirect("/addnew");
  });
});

// layer lookup
app.get("/addnew", (req, res) => {
  let layer = parseInt(req.query.layer ?? 0, 10);
  if (!newVetex[layer]) newVetex[layer] = [];

  const layers = getSortedLayers();
  const currentIndex = layers.indexOf(layer);

  const behindLayer = layers[currentIndex - 1];
  const afterLayer = layers[currentIndex + 1];

  res.render("addnew.html", {
    sprite: newSprite,
    layer,
    behindpoints: behindLayer !== undefined ? newVetex[behindLayer] : [],
    points: newVetex[layer],
    afterpoints: afterLayer !== undefined ? newVetex[afterLayer] : [],
    newVetex
  });
});

app.post("/savelayer", (req, res) => {
  const layer = parseInt(req.body.layer, 10) || 0;
  const points = Array.isArray(req.body.points) ? req.body.points : req.body.points ? [req.body.points] : [];
  newVetex[layer] = points;
  res.redirect(`/addnew?layer=${encodeURIComponent(layer)}`);
});

app.post("/nextlayer", (req, res) => {
  const layer = parseInt(req.body.layer, 10) || 0;
  const height = parseInt(req.body.height, 10) || 1;
  const nextLayer = layer + height;

  if (!newVetex[nextLayer]) newVetex[nextLayer] = [];

  console.log("Current layers:", getSortedLayers().map(k => `Layer ${k}: ${JSON.stringify(newVetex[k])}`));
  res.redirect(`/addnew?layer=${encodeURIComponent(nextLayer)}`);
});

//layer lookup for edge-making
app.get("/makeedge", (req, res) => {
  let layer = parseInt(req.query.layer ?? 0, 10);
  const layers = getSortedLayers();
  const currentIndex = layers.indexOf(layer);

  const behindLayer = layers[currentIndex - 1];
  const afterLayer = layers[currentIndex + 1];

  res.render("makeedge.html", {
    sprite: newSprite,
    layer,
    behindpoints: behindLayer !== undefined ? newVetex[behindLayer] : [],
    points: newVetex[layer] || [],
    afterpoints: afterLayer !== undefined ? newVetex[afterLayer] : [],
    newVetex,
    selectpoint: tempPoint[layer] || [],
    newEdges
  });
});

app.post("/pointsave", (req, res) => {
  const layer = parseInt(req.body.layer, 10) || 0;
  const points = Array.isArray(req.body.points) ? req.body.points : req.body.points ? [req.body.points] : [];

  if (Object.keys(tempPoint).length === 0) {
    tempPoint[layer] = points;
  } else {
    const storedLayer = parseInt(Object.keys(tempPoint)[0], 10);
    const point1 = [...JSON.parse(tempPoint[storedLayer]), storedLayer];
    const point2 = [...JSON.parse(points), layer];

    newEdges.push(JSON.stringify([JSON.stringify(point1), JSON.stringify(point2)]));
    tempPoint = {};
  }
  res.redirect(`/makeedge?layer=${encodeURIComponent(layer)}`);
});

app.post("/saveall", (req, res) => {
  if (!newSprite) {
    return res.redirect(`/?error=${encodeURIComponent("No sprite to save")}`);
  }

  const edgesJSON = JSON.stringify(newEdges);

  const vertexpoints = Object.entries(newVetex).flatMap(([layer, coords]) =>
    coords.map(c => [...JSON.parse(c), parseInt(layer, 10)])
  );

  const vetexJSON = JSON.stringify(vertexpoints);

  db.run(
    "INSERT INTO Sprite (SpriteID, Edges, Vetex) VALUES (?, ?, ?)",
    [newSprite, edgesJSON, vetexJSON],
    (err) => {
      if (err) {
        console.error(err.message);
        return res.status(500).send("Database error");
      }
      // Reset temp state
      newSprite = "";
      newEdges = [];
      newVetex = {};
      tempPoint = {};
      res.redirect(`/?error=${encodeURIComponent("Sprite saved successfully")}`);
    }
  );
});

app.listen(port, () => {
  console.log(`Server running at http://localhost:${port}`);
});
