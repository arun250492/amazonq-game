import pygame
import sys
import random
import math

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 5
        self.health = 100
        self.has_weapon = False
        self.weapon_type = None
        self.damage = 10  # Default damage
        self.color = BLUE
        
    def update(self, keys, weapons, zone):
        # Movement
        if keys[pygame.K_w] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_s] and self.y < SCREEN_HEIGHT - self.height:
            self.y += self.speed
        if keys[pygame.K_a] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_d] and self.x < SCREEN_WIDTH - self.width:
            self.x += self.speed
        
        # Check for weapon pickup
        for weapon in weapons[:]:
            if (abs(self.x - weapon.x) < 30 and abs(self.y - weapon.y) < 30):
                self.has_weapon = True
                self.weapon_type = weapon.weapon_type
                self.damage = weapon.damage
                weapons.remove(weapon)
    
    def shoot(self, enemies):
        if not self.has_weapon:
            return
        
        # Simple shooting mechanic - hit closest enemy in range
        closest_enemy = None
        min_distance = 200  # Maximum shooting range
        
        for enemy in enemies:
            distance = math.sqrt((self.x - enemy.x)**2 + (self.y - enemy.y)**2)
            if distance < min_distance:
                min_distance = distance
                closest_enemy = enemy
        
        if closest_enemy:
            closest_enemy.take_damage(self.damage)
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Health bar
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, self.width * (self.health / 100), 5))

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 2
        self.health = 100
        self.has_weapon = False
        self.weapon_type = None
        self.damage = 5  # Default damage
        self.color = RED
        self.shoot_cooldown = 0
        
    def update(self, player, weapons, zone):
        # Simple AI: move towards player if far, move randomly if close
        distance_to_player = math.sqrt((self.x - player.x)**2 + (self.y - player.y)**2)
        
        if distance_to_player > 200:
            # Move towards player
            dx = player.x - self.x
            dy = player.y - self.y
            dist = math.sqrt(dx*dx + dy*dy)
            if dist != 0:
                dx, dy = dx/dist, dy/dist
            self.x += dx * self.speed
            self.y += dy * self.speed
        else:
            # Move randomly
            self.x += random.choice([-1, 0, 1]) * self.speed
            self.y += random.choice([-1, 0, 1]) * self.speed
        
        # Keep within screen bounds
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))
        self.y = max(0, min(self.y, SCREEN_HEIGHT - self.height))
        
        # Check for weapon pickup
        for weapon in weapons[:]:
            if (abs(self.x - weapon.x) < 30 and abs(self.y - weapon.y) < 30):
                self.has_weapon = True
                self.weapon_type = weapon.weapon_type
                self.damage = weapon.damage
                weapons.remove(weapon)
        
        # Shoot at player if has weapon and in range
        if self.has_weapon and distance_to_player < 150:
            if self.shoot_cooldown <= 0:
                player.take_damage(self.damage)
                self.shoot_cooldown = 60  # Cooldown in frames
            else:
                self.shoot_cooldown -= 1
    
    def take_damage(self, amount):
        self.health -= amount
        if self.health < 0:
            self.health = 0
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # Health bar
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, self.width * (self.health / 100), 5))

class Weapon:
    def __init__(self, x, y, weapon_type):
        self.x = x
        self.y = y
        self.weapon_type = weapon_type
        
        # Set damage based on weapon type
        if weapon_type == "pistol":
            self.damage = 20
            self.color = BLACK
        elif weapon_type == "rifle":
            self.damage = 35
            self.color = BROWN
        elif weapon_type == "shotgun":
            self.damage = 50
            self.color = WHITE
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, 15, 15))

class Zone:
    def __init__(self, screen_width, screen_height):
        self.max_radius = int(math.sqrt(screen_width**2 + screen_height**2) / 2)
        self.current_radius = self.max_radius
        self.center_x = screen_width // 2
        self.center_y = screen_height // 2
        self.shrink_rate = 0.2
        self.shrink_timer = 0
        self.shrink_interval = 300  # Frames between shrinks
    
    def update(self):
        self.shrink_timer += 1
        if self.shrink_timer >= self.shrink_interval:
            self.shrink_timer = 0
            self.current_radius = max(100, self.current_radius - self.shrink_rate * self.max_radius)
    
    def is_inside(self, x, y):
        distance = math.sqrt((x - self.center_x)**2 + (y - self.center_y)**2)
        return distance <= self.current_radius
    
    def draw(self, screen):
        # Draw safe zone circle
        pygame.draw.circle(screen, BLUE, (self.center_x, self.center_y), int(self.current_radius), 2)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Python Battle Royale")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "menu"  # menu, playing, game_over
        self.font = pygame.font.SysFont(None, 36)
        
        # Game objects
        self.player = None
        self.enemies = []
        self.weapons = []
        self.zone = None
        
        # Game stats
        self.kills = 0
        self.players_left = 0
        
    def init_game(self):
        # Create player
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # Create enemies
        self.enemies = []
        self.players_left = 10  # Including the player
        for _ in range(self.players_left - 1):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            # Ensure enemies don't spawn too close to player
            while math.sqrt((x - self.player.x)**2 + (y - self.player.y)**2) < 150:
                x = random.randint(50, SCREEN_WIDTH - 50)
                y = random.randint(50, SCREEN_HEIGHT - 50)
            self.enemies.append(Enemy(x, y))
        
        # Create weapons on the map
        self.weapons = []
        for _ in range(5):
            x = random.randint(50, SCREEN_WIDTH - 50)
            y = random.randint(50, SCREEN_HEIGHT - 50)
            weapon_type = random.choice(["pistol", "rifle", "shotgun"])
            self.weapons.append(Weapon(x, y, weapon_type))
        
        # Create the zone
        self.zone = Zone(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Reset stats
        self.kills = 0
        self.game_state = "playing"
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            if self.game_state == "menu":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.init_game()
            
            elif self.game_state == "playing":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.player.shoot(self.enemies)
            
            elif self.game_state == "game_over":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    self.game_state = "menu"
    
    def update(self):
        if self.game_state == "playing":
            # Update player
            keys = pygame.key.get_pressed()
            self.player.update(keys, self.weapons, self.zone)
            
            # Update enemies
            for enemy in self.enemies[:]:
                enemy.update(self.player, self.weapons, self.zone)
                
                # Check if enemy is dead
                if enemy.health <= 0:
                    self.enemies.remove(enemy)
                    self.kills += 1
                    self.players_left -= 1
            
            # Update zone
            self.zone.update()
            
            # Check if player is outside zone
            if not self.zone.is_inside(self.player.x, self.player.y):
                self.player.take_damage(0.5)  # Zone damage
            
            # Check if player is dead
            if self.player.health <= 0:
                self.game_state = "game_over"
            
            # Check if player is the last one standing
            if len(self.enemies) == 0:
                self.game_state = "game_over"
    
    def render(self):
        self.screen.fill(GREEN)  # Background color (grass)
        
        if self.game_state == "menu":
            title = self.font.render("Python Battle Royale", True, BLACK)
            instruction = self.font.render("Press ENTER to start", True, BLACK)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2))
        
        elif self.game_state == "playing":
            # Draw zone
            self.zone.draw(self.screen)
            
            # Draw weapons
            for weapon in self.weapons:
                weapon.draw(self.screen)
            
            # Draw enemies
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            # Draw player
            self.player.draw(self.screen)
            
            # Draw HUD
            health_text = self.font.render(f"Health: {int(self.player.health)}", True, BLACK)
            weapon_text = self.font.render(f"Weapon: {self.player.weapon_type if self.player.has_weapon else 'None'}", True, BLACK)
            kills_text = self.font.render(f"Kills: {self.kills}", True, BLACK)
            players_text = self.font.render(f"Players left: {self.players_left}", True, BLACK)
            
            self.screen.blit(health_text, (10, 10))
            self.screen.blit(weapon_text, (10, 50))
            self.screen.blit(kills_text, (10, 90))
            self.screen.blit(players_text, (10, 130))
        
        elif self.game_state == "game_over":
            if self.player.health > 0:
                result = self.font.render("WINNER WINNER CHICKEN DINNER!", True, BLACK)
            else:
                result = self.font.render("GAME OVER", True, BLACK)
            
            stats = self.font.render(f"Kills: {self.kills}", True, BLACK)
            instruction = self.font.render("Press ENTER to return to menu", True, BLACK)
            
            self.screen.blit(result, (SCREEN_WIDTH // 2 - result.get_width() // 2, SCREEN_HEIGHT // 3))
            self.screen.blit(stats, (SCREEN_WIDTH // 2 - stats.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        pygame.display.flip()
    
    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()