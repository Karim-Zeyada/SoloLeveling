# Solo Leveling Game

A strategy/stealth game inspired by *Solo Leveling*, where you play as a rogue AI navigating a corporate firewall.

## 🎮 Game Overview
You are infiltrating a secure system. Your goal is to collect DATA nodes (resources), avoid or defeat SECURITY AGENTS (enemies), and reach the EXIT to advance to the next system layer. You can build walls and traps, or summon Shadows to fight for you.

## ✨ Key Features
*   **Isometric View**: 2.5D grid-based world.
*   **Tactical Combat**: Summon specific Shadows (Igris, Beru) to fight enemies.
*   **Trap System**: Place Bind, Spike, or Gravity traps to control the battlefield.
*   **Stealth & Vision**: Fog of War mechanic requires scanning to reveal the map.
*   **Pathfinding**: A* algorithm for movement.
*   **5 Levels**: Progressively harder levels with different enemy types (Security Agents, Elves, Alpha Bears).

## 🕹️ Controls
*   **Arrow Keys** / **WASD**: Move Player using grid steps.
*   **Mouse Click**: Move Player using Pathfinding (auto-walk).
*   **Space**: Scan area (reveal fog).
*   **B**: Build Wall.
*   **T**: Open **Trap Selection Menu**.
*   **R**: Open **Shadow Summon Menu**.
*   **U**: Dismiss last Shadow (refunds cost).
*   **F**: Toggle Shadow Attack Mode.
*   **ESC**: Pause / Close Menu.

## 🛠️ Installation & Run
1.  **Install Python 3.x**.
2.  **Create Virtual Environment**:
    ```bash
    python -m venv venv
    venv\Scripts\activate  # Windows
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Game**:
    ```bash
    python main.py
    ```

## 🧠 AI Concepts Implemented
*   **A* Pathfinding**: Used for player and enemy navigation.
*   **Finite State Machines (FSM)**: Enemy behavior (Idle -> Patrol -> Chase).
*   **Breadth-First Search (BFS)**: Used for "Scan" ability to reveal Fog of War.

## 📂 Project Structure
*   `assets/`: Game images and sounds.
*   `config/`: Game settings and constants.
*   `core/`: Core engine utilities (logger, state machine).
*   `entities/`: Game objects (Player, Enemy, Tile).
*   `managers/`: Asset and Sound managers.
*   `rendering/`: Isometric renderer and camera.
*   `states/`: Game states (Playing, Menu).
*   `systems/`: Algorithms (Pathfinding, Input).
*   `ui/`: User Interface classes.

