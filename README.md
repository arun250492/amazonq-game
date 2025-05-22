# Python Battle Royale

A simplified PUBG-like battle royale game built with Python and Pygame.

## Features

- 2D top-down battle royale gameplay
- Player movement with WASD keys
- Weapon pickups (pistol, rifle, shotgun)
- Enemy AI that hunts the player
- Shrinking play zone (like PUBG's circle)
- Health system and combat mechanics

## How to Play

1. Install the requirements:
   ```
   pip install -r requirements.txt
   ```

2. Run the game:
   ```
   python main.py
   ```

3. Controls:
   - WASD: Move player
   - SPACE: Shoot
   - ENTER: Start game / Return to menu after game over

## Game Mechanics

- Pick up weapons to increase your damage
- Stay inside the blue circle to avoid taking damage
- Eliminate all enemies to win
- If your health reaches zero, it's game over

## Game Objects

- Player (blue square): You control this character
- Enemies (red squares): AI-controlled opponents
- Weapons (various colored squares): Pick these up to increase your damage
- Zone (blue circle): Stay inside this circle to avoid damage

Enjoy the game!
