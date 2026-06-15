*This project has been created as part of the 42 curriculum by Zawarudo20.*

---

## Description

**fly-in** is an interactive drone traffic management and pathfinding visualization system. The project simulates complex logistics scenarios where multiple drones must navigate through interconnected hubs (nodes) with capacity constraints, restricted zones, and priority pathways. It combines graph-based pathfinding algorithms with real-time visualization to demonstrate efficient resource allocation and congestion management in constrained environments.

The core goal is to route drones from a start hub to a goal hub while respecting:
- **Hub capacity limits**: Maximum number of drones that can occupy each hub simultaneously
- **Link capacity limits**: Maximum number of drones that can traverse connections between hubs
- **Zone restrictions**: Special zones (normal, blocked, restricted, priority) with different traversal costs
- **Dynamic pathfinding**: Drones adaptively route around congested areas to optimize throughput

---

## Features

- **Visual Network Simulation**: Real-time pygame-based visualization of drone movement through a multi-hub network
- **Intelligent Pathfinding**: A* and Dijkstra-inspired pathfinding with dynamic cost adjustments based on zone types and congestion
- **Configuration-Driven Scenarios**: Define custom drone networks, hub layouts, and constraints via human-readable config files
- **Capacity Management**: Track and enforce capacity limits on both hubs and connections
- **Zone-Based Routing**: Support for multiple zone types (normal, restricted, priority, blocked) with different traversal penalties
- **Interactive UI**: Menu system with music controls, start/exit buttons, and hub information cards
- **Animated Drones**: Sprite-based drone animations for engaging visual feedback

---

## Instructions

### Compilation & Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Zawarudo20/fly-in.git
   cd fly-in
   ```

2. **Install dependencies**:
   ```bash
   make install
   ```
   This installs the required packages from `requirements.txt`:
   - `pygame-ce` - Community Edition of Pygame for rendering and events
   - `webcolors` - CSS color name to RGB conversion
   - `pydantic` - Data validation and modeling
   - `flake8` - Code linting
   - `mypy` - Static type checking

3. **Verify setup** (optional lint and type checking):
   ```bash
   make lint
   ```

### Running the Application

Execute the program with a configuration file:

```bash
make run
```

Or run directly:

```bash
python3 Script/Fly_in.py config.txt
```

To use a custom config:

```bash
python3 Script/Fly_in.py your_config_file.txt
```

### Debugging

For interactive debugging with the Python debugger:

```bash
make debug
```

### Cleaning

Remove cache files and compiled bytecode:

```bash
make clean
```

---

## Algorithm & Implementation Strategy

### Pathfinding Algorithm

The project employs a **dynamic A*-inspired pathfinding** algorithm with zone-aware cost functions:

1. **Cost Calculation Per Zone**:
   - `normal` zone: `g = current.g + 2` (baseline cost)
   - `restricted` zone: `g = current.g + 4` (high penalty for narrow passages)
   - `priority` zone: `g = current.g + 1.5` (low cost for fast lanes)
   - `blocked` zone: skipped entirely (impassable)

2. **Congestion-Aware Routing**:
   - If a hub or connection is at capacity, additional cost `+2` is applied
   - Drones recalculate paths when blocked, avoiding jams dynamically
   - The algorithm maintains visited nodes and updates path costs if a better route is found

3. **Path Reconstruction**:
   - Each hub stores a `path` reference to its predecessor
   - Starting from the goal, backtrack through predecessors to build the optimal route
   - Drones follow this pre-computed path, updating it when blocked

### Data Model

**Hub**: Represents a location in the network
- Position (x, y)
- Color (for visualization)
- Capacity (max simultaneous drones)
- Zone type (normal/restricted/priority/blocked)
- Visitor tracking (current drones present)
- Connections to other hubs

**Line**: Represents a connection between two hubs
- Capacity (max drones traversing at once)
- Position (midpoint for visualization)
- Visitor tracking

**Drone**: Individual agent navigating the network
- Current hub and goal hub
- Computed path and current progress along that path
- Animation state (sprite index)
- Movement interpolation (smooth animation between hubs)

**Map**: Graph container
- Manages all hubs, lines, and drones
- Enforces global constraints during updates
- Computes min/max bounds for rendering

### Update Cycle

Each frame:
1. **Drone Movement Interpolation**: Update sprite position along current path segment
2. **Congestion Check**: For each drone, evaluate if it can move to the next hub
   - Check hub capacity
   - Check connection capacity
   - Check downstream hub availability
3. **Pathfinding Trigger**: If blocked, run pathfinding to find an alternative
4. **Hub/Line Update**: Add/remove drone from visitor sets as it progresses

---

## Visual Representation & User Experience

### Rendering System

- **Screen Resolution**: 1200×700 pixels
- **Grid-Based Layout**: Hubs positioned on a discrete 2D grid
- **Color-Coded Hubs**:
  - Start hub (green) – initial position for all drones
  - Goal hub (green) – destination for all drones
  - Normal hubs (varied colors) – standard waypoints
  - Restricted zones (red) – slow, capacity-limited paths
  - Priority zones (cyan) – fast, limited-capacity bypass routes
  - Waiting areas (blue) – queue management zones
  - Convergence points (yellow) – merge points with congestion

### Interactive Elements

- **Main Menu**:
  - Start button: Launch simulation
  - Music toggle: Enable/disable background music
  - Exit button: Quit application
  
- **In-Game Menu** (Press SPACE):
  - Resume simulation
  - Music control (toggle audio)
  - Exit to main menu

- **Hover Information**: Each hub displays:
  - Hub name
  - Position (x, y)
  - Current occupancy vs. capacity
  - Zone type

### Animated Elements

- **Drone Sprites**: 8-frame animation cycle (0–7) with configurable delays
- **Smooth Movement**: Non-linear interpolation between hubs with configurable speed
- **Visual Feedback**: Drone color reflects state (moving/waiting/completed)

### UX Enhancements

- **Real-Time Status**: Display active drone count, throughput metrics, and congestion levels
- **Visual Congestion**: Hub and connection colors intensify as capacity approaches limits
- **Sound Design**:
  - Background menu music for ambiance
  - Click sounds for UI interactions
  - Error sounds for invalid actions
- **Minecraft Font**: Retro pixelated aesthetic for immersion

---

## Configuration File Format

Define your drone network and constraints in a `.txt` configuration file:

```
nb_drones: <integer>

start_hub: <name> <x> <y> [color=<color> max_drones=<int>]
end_hub: <name> <x> <y> [color=<color> max_drones=<int>]
hub: <name> <x> <y> [color=<color> max_drones=<int> zone=<zone>]

connection: <hub1>-<hub2> [max_link_capacity=<int>]
```

### Metadata Options

**Hub Metadata**:
- `color`: CSS color name (e.g., orange, blue, red, cyan, yellow)
- `max_drones`: Maximum capacity for this hub
- `zone`: One of [normal, restricted, priority, blocked]

**Connection Metadata**:
- `max_link_capacity`: Maximum drones traversing this connection simultaneously (default: 1)

### Example

See `config.txt` for a complex hard-mode scenario with:
- 12 drones
- Multiple sequential gates (bottlenecks)
- Restricted tunnels and priority bypass routes
- Waiting areas for queue management
- Final convergence point testing throughput limits

---

## Resources

### Documentation & References

- **Pygame Community Edition**: https://pyga.me/
  - Comprehensive guide on game rendering, event handling, and sprite management
  
- **Pydantic v2**: https://docs.pydantic.dev/
  - Data validation and type-safe configuration parsing
  
- **Graph Algorithms**: 
  - A* Pathfinding: https://en.wikipedia.org/wiki/A*_search_algorithm
  - Dijkstra's Algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
  
- **Constraint Satisfaction Problems (CSPs)**:
  - Multi-agent pathfinding with capacity constraints: https://en.wikipedia.org/wiki/Multi-agent_pathfinding

### AI Usage

AI (ChatGPT) was consulted for:

1. **Algorithm Optimization**: Refining A* implementation to handle zone-based costs and dynamic replanning
2. **Pydantic Validation**: Designing robust config file parsing with custom validators for color names and zone types
3. **Pygame Integration**: Structuring the visualization layer, sprite animation logic, and event-driven UI
4. **Code Structure**: Organizing modules (Hubs, Drones, Visualization) for maintainability and separation of concerns
5. **Documentation**: Generating comprehensive docstrings and this README to explain implementation details

The core algorithmic design (zone-aware costs, capacity constraints, dynamic pathfinding) was authored independently.

---

## Project Structure

```
fly-in/
├── Script/
│   ├── Fly_in.py           # Entry point; initializes parser, solver, and main menu
│   ├── Parsing.py          # Config file parser with error handling
│   ├── Hubs.py             # Hub, Line, and Map data models
│   ├── Drones.py           # Drone pathfinding and update logic
│   ├── Visualization.py    # Main menu and game visualization
│   ├── Fly_in_utils.py     # UI utilities (Menu, Card, etc.)
│   └── pygame_utils.py     # Pygame helpers (Animation, Movement, Button)
├── assets/                 # Images, sprites, fonts, sounds
│   ├── Drone/              # Drone animation frames
│   ├── main_menu/          # Menu UI images
│   ├── font/               # Minecraft.ttf
│   └── sounds/             # Background music and SFX
├── config.txt              # Example configuration
├── requirements.txt        # Python dependencies
├── Makefile                # Build and execution targets
└── README.md               # This file
```

---

## Future Enhancements

- [ ] Statistics dashboard (throughput, average wait time, bottleneck analysis)
- [ ] Custom config generator UI
- [ ] Replay/recording system for successful runs
- [ ] Performance profiling for large-scale simulations
- [ ] Multi-objective optimization (minimize time vs. energy consumption)
- [ ] Network topology learning and adaptation

---

**Enjoy exploring the fly-in drone traffic management system!** 🚁
