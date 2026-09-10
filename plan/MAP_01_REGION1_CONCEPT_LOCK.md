# MAP 01 / REGION 1 — CONCEPT LOCK

Date: 2026-09-10
Branch: `r3-map-camera`
Status: **CONCEPT APPROVED / OLD R3 ART REJECTED**

## 1. Master reference

Approved visual master reference:
`PROJECT_SOURCE/references/MAP_01_VISUAL_REFERENCE_APPROVED.png`

SHA-256:
`8871a7132c4e2915008e0ee217b8240c6bf26f95a0c4edce0566ea6dcdabf56b`

This image is the authoritative composition and mood reference for the first playable map / Region 1.
It is not a ready runtime asset and must not be crudely tiled or down-converted as a shortcut.

## 2. Artistic priority

For the rebuild of Map 01, visual quality and coherent geography have priority over the old R3 tile-reuse targets.
The art-authoring stage is intentionally **not constrained by the previous palette-count, tile-reuse, block-count, or percentage-matching targets**.
Do not reduce the map to fit an arbitrary visual metric.
If a technical runtime limitation conflicts with the approved composition, solve the runtime representation/streaming problem rather than degrading the world design.

Forbidden as an authoring method:
- procedural terrain generation;
- repeated rectangular stamps used to build geography;
- visible chunk seams;
- carpet-like repeated forests;
- copied house/ruin blocks repeated without manual variation;
- using “% of accepted R2 tiles” as a quality gate.

Allowed automation is limited to technical support after the art exists: slicing, lossless transport, palette analysis, conversion, collision export, compression, build verification and regression tests.

## 3. Region 1 large-scale geography

The complete map must read as one connected landscape when viewed from far above.

### Northwest — ruined settlement / fortress remains
A large ruined zone embedded into forest and rocky ground. It must have irregular outer edges, multiple distinct ruin shapes, debris, broken routes and at least two possible approaches. It is a major combat/exploration landmark, not a repeated decorative stamp.

### North / north-center — river source and waterfall
The river begins in elevated rocky terrain and descends through a visible waterfall/rapid section. This is a strong navigational landmark. The river must retain a continuous natural course from source to downstream wetlands.

### Northeast — isolated homestead
A visually distinct house/farmstead in a clearing, separated from the central village. It has its own short access road, yard/fence and surrounding forest/rock context.

### Center — main village and road hub
The primary settlement and navigation anchor of Region 1. Multiple roads converge here. It must read as a unique settlement with a central open space, several non-identical buildings, service/mission space and clear exits toward the other regions of the map.

### East / center-east — farm fields and bridge corridor
Open terrain, cultivated plots, farm objects and one of the principal bridge crossings. This is intentionally more open than the forest sectors and supports long sight lines and vehicle movement.

### Southeast — wetlands / marsh
A darker, visually distinct water-and-reed area. It contains irregular channels, shallow water, dry islands and constrained routes. It must transition naturally from the main river instead of appearing as a separate pasted square.

### South / southwest — rural roads and farms
Lower-density settlement, one or more isolated farms, winding roads and clearings. This area provides a calmer visual rhythm between dense forest and major landmarks.

### West / southwest — forest lake and bypass route
A lake/river widening with irregular shoreline, small islands/rocks and a secondary route through forest. It provides an alternate traversal path and a strong visual contrast to the central village.

## 4. Road network

The road network must be continuous and intentional:
- one primary route links the central village with the principal crossings;
- secondary roads branch toward the ruins, isolated homestead, farms and southern route;
- roads widen/merge naturally at junctions;
- bridge approaches align with road direction;
- roads may narrow or become tracks in forest but must never terminate arbitrarily at tile/chunk borders.

## 5. River and bridges

The river is the main geographic spine of Region 1.
Requirements:
- one continuous winding river system;
- visible source/waterfall in the north;
- varying width, banks and current character;
- 2–3 meaningful bridge crossings;
- downstream transition into wetlands in the southeast;
- no square water patches disconnected from river logic.

## 6. Forest language

Forests must be authored as irregular masses, not rectangles.
Use:
- uneven edge depth;
- clearings;
- sparse transition belts;
- occasional rocks/stumps/dead trees;
- local density changes;
- narrow road corridors and natural openings.

No two large forest sectors should share an obviously repeated silhouette.

## 7. Landmark hierarchy

Major landmarks, in descending visual importance:
1. central village;
2. north waterfall / river source;
3. northwest ruins;
4. main bridge corridor;
5. southeast wetlands;
6. west/southwest lake;
7. isolated homestead;
8. rural farms and minor clearings.

The player should be able to infer approximate location from the environment without relying on coordinate text.

## 8. Gameplay-space intent

The approved overview becomes the spatial blueprint for later gameplay layers:
- collision/navigation;
- roads and movement modifiers;
- water/deep water;
- bridge traversal;
- marsh slowdown;
- building/rock/tree blocking;
- encounter zones;
- mission triggers;
- NPC/vehicle spawn areas;
- entrances/exits to future regions.

These gameplay layers are separate from the master artwork and must conform to its geography, not reshape it for convenience.

## 9. Existing R3 technology that may be retained

Retain only proven technical systems that do not force the old visual result:
- smooth camera logic;
- camera bounds;
- MAP/world streaming concepts;
- fixed HUD separation;
- NTSC/PAL timing work;
- build/reproducibility/emulator test infrastructure.

The current old R3 Region 1 artwork/geography is **not** a visual source for the rebuild except where a single motif is manually redrawn/reused deliberately.

## 10. Acceptance gate for this concept stage

Concept stage is complete when the project contains:
- the approved full-map reference by hash;
- this locked geography description;
- explicit rejection of the old block/stamp construction method;
- explicit instruction that later technical conversion must preserve the approved world composition.

**MAP 01 / REGION 1 CONCEPT: LOCKED.**

Next stage after a separate user command: **B — create the production master map at high resolution and turn this overview into a clean, manually authored world layout before any runtime slicing/conversion.**
