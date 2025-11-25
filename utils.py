import pygame
import random
import numpy as np
import math
import os

# Game Constants
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 700
FPS = 60

# Premium Color Palette
DEEP_SPACE = (5, 5, 15)
STAR_WHITE = (255, 255, 255)
STAR_BLUE = (173, 216, 230)
STAR_YELLOW = (255, 253, 208)
NEBULA_PURPLE = (138, 43, 226, 30)
NEBULA_BLUE = (0, 191, 255, 20)
NEON_CYAN = (0, 255, 255)
NEON_PINK = (255, 20, 147)
NEON_GREEN = (57, 255, 20)
NEON_ORANGE = (255, 165, 0)

class ParticleSystem:
    """Premium particle effects"""
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, color, count=5, speed_range=(1, 3)):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            self.particles.append({
                'x': x,
                'y': y,
                'vx': vx,
                'vy': vy,
                'life': 30,
                'max_life': 30,
                'color': color,
                'size': random.randint(2, 4)
            })
    
    def update(self):
        for p in self.particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            p['vy'] += 0.1  # gravity
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def draw(self, screen):
        for p in self.particles:
            alpha = int(255 * (p['life'] / p['max_life']))
            size = int(p['size'] * (p['life'] / p['max_life']))
            if size > 0:
                color = (*p['color'][:3], alpha)
                # Draw with glow effect
                for i in range(3):
                    s = pygame.Surface((size * 2 + i*2, size * 2 + i*2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (*p['color'][:3], alpha // (i+1)), 
                                     (size + i, size + i), size + i)
                    screen.blit(s, (p['x'] - size - i, p['y'] - size - i))

class StarField:
    """Multi-layer parallax star field"""
    def __init__(self):
        self.layers = []
        # Create 3 layers of stars
        for layer in range(3):
            stars = []
            count = 80 - layer * 20
            speed = (layer + 1) * 0.5
            size_range = (1 + layer, 3 + layer)
            
            for _ in range(count):
                stars.append({
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(0, SCREEN_HEIGHT),
                    'size': random.randint(*size_range),
                    'speed': speed,
                    'color': random.choice([STAR_WHITE, STAR_BLUE, STAR_YELLOW]),
                    'twinkle': random.randint(0, 100)
                })
            self.layers.append(stars)
    
    def update(self):
        for layer in self.layers:
            for star in layer:
                star['y'] += star['speed']  # Move DOWN (we're going UP)
                star['twinkle'] = (star['twinkle'] + 1) % 100
                if star['y'] > SCREEN_HEIGHT:
                    star['y'] = 0
                    star['x'] = random.randint(0, SCREEN_WIDTH)
    
    def draw(self, screen):
        for layer in self.layers:
            for star in layer:
                # Twinkle effect
                brightness = 200 + int(55 * math.sin(star['twinkle'] * 0.1))
                color = tuple(min(255, int(c * brightness / 255)) for c in star['color'][:3])
                pygame.draw.circle(screen, color, (int(star['x']), int(star['y'])), star['size'])

class NebulaClouds:
    """Animated nebula clouds in background"""
    def __init__(self):
        self.clouds = []
        for _ in range(5):
            self.clouds.append({
                'x': random.randint(-100, SCREEN_WIDTH + 100),
                'y': random.randint(-100, SCREEN_HEIGHT + 100),
                'size': random.randint(150, 300),
                'speed': random.uniform(0.1, 0.3),
                'color': random.choice([NEBULA_PURPLE, NEBULA_BLUE])
            })
    
    def update(self):
        for cloud in self.clouds:
            cloud['y'] += cloud['speed']
            if cloud['y'] > SCREEN_HEIGHT + 100:
                cloud['y'] = -100
                cloud['x'] = random.randint(-100, SCREEN_WIDTH + 100)
    
    def draw(self, screen):
        for cloud in self.clouds:
            s = pygame.Surface((cloud['size'], cloud['size']), pygame.SRCALPHA)
            pygame.draw.circle(s, cloud['color'], 
                             (cloud['size']//2, cloud['size']//2), 
                             cloud['size']//2)
            screen.blit(s, (cloud['x'] - cloud['size']//2, cloud['y'] - cloud['size']//2))

def load_and_scale_image(path, size):
    """Load image with fallback to procedural generation"""
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except:
        return None

def create_procedural_rocket(size):
    """Create better looking procedural rocket"""
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    
    # Body (pointing UP)
    points_body = [
        (size//2, 5),              # nose
        (size//2 + 15, size - 10), # right side
        (size//2, size - 5),       # bottom center
        (size//2 - 15, size - 10)  # left side
    ]
    pygame.draw.polygon(surf, (200, 200, 200), points_body)
    pygame.draw.polygon(surf, NEON_CYAN, points_body, 3)
    
    # Window
    pygame.draw.circle(surf, (100, 200, 255), (size//2, size//2), 6)
    pygame.draw.circle(surf, NEON_CYAN, (size//2, size//2), 6, 2)
    
    # Wings
    wing_left = [(size//2 - 15, size - 15), (size//2 - 30, size), (size//2 - 15, size - 5)]
    wing_right = [(size//2 + 15, size - 15), (size//2 + 30, size), (size//2 + 15, size - 5)]
    pygame.draw.polygon(surf, (150, 150, 150), wing_left)
    pygame.draw.polygon(surf, (150, 150, 150), wing_right)
    pygame.draw.polygon(surf, NEON_PINK, wing_left, 2)
    pygame.draw.polygon(surf, NEON_PINK, wing_right, 2)
    
    return surf

def create_procedural_asteroid(size, variant=1):
    """Create better looking procedural asteroid"""
    surf = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    
    # Base colors
    colors = [
        (139, 69, 19),   # brown
        (105, 105, 105), # gray
        (160, 82, 45),   # sienna
    ]
    base_color = colors[variant % 3]
    
    # Create jagged circle
    num_points = random.randint(8, 12)
    points = []
    for i in range(num_points):
        angle = (360 / num_points) * i + random.randint(-15, 15)
        radius = size + random.randint(-size//4, size//4)
        px = size + radius * math.cos(math.radians(angle))
        py = size + radius * math.sin(math.radians(angle))
        points.append((px, py))
    
    # Draw asteroid
    pygame.draw.polygon(surf, base_color, points)
    
    # Add detail craters
    for _ in range(random.randint(3, 6)):
        cx = random.randint(size//2, size + size//2)
        cy = random.randint(size//2, size + size//2)
        crater_size = random.randint(size//6, size//3)
        darker = tuple(max(0, c - 40) for c in base_color)
        pygame.draw.circle(surf, darker, (cx, cy), crater_size)
    
    # Outline
    pygame.draw.polygon(surf, (80, 80, 80), points, 2)
    
    return surf

class Rocket:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 100
        self.size = 50
        self.vx = 0
        self.vy = 0
        self.max_speed = 6
        self.angle = 0  # for rotation
        self.particles = ParticleSystem()
        
        # Load or create sprite
        self.image = load_and_scale_image('assets/rocket.png', (self.size, self.size))
        if self.image is None:
            self.image = create_procedural_rocket(self.size)
    
    def update(self, action):
        # action: 0=nothing, 1=up, 2=down, 3=left, 4=right
        self.vx *= 0.85  # friction
        self.vy *= 0.85
        
        if action == 1:
            self.vy = -self.max_speed
            # Emit thrust particles DOWN (we're going UP)
            self.particles.emit(self.x, self.y + self.size//2, NEON_ORANGE, 3, (1, 2))
        elif action == 2:
            self.vy = self.max_speed
        elif action == 3:
            self.vx = -self.max_speed
            self.angle = -15  # tilt left
        elif action == 4:
            self.vx = self.max_speed
            self.angle = 15  # tilt right
        else:
            self.angle *= 0.9  # return to center
        
        self.x += self.vx
        self.y += self.vy
        
        # Keep in bounds
        self.x = max(self.size//2, min(SCREEN_WIDTH - self.size//2, self.x))
        self.y = max(self.size//2, min(SCREEN_HEIGHT - self.size//2, self.y))
        
        self.particles.update()
    
    def draw(self, screen):
        # Draw thrust particles first (behind rocket)
        self.particles.draw(screen)
        
        # Draw rocket with rotation
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=(self.x, self.y))
        
        # Glow effect
        glow_surf = pygame.Surface((self.size + 20, self.size + 20), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*NEON_CYAN[:3], 30), 
                          (self.size//2 + 10, self.size//2 + 10), self.size//2 + 10)
        screen.blit(glow_surf, (self.x - self.size//2 - 10, self.y - self.size//2 - 10))
        
        screen.blit(rotated, rect)

class Asteroid:
    def __init__(self, x, y, vx, vy, size, variant=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(-2, 2)
        self.variant = variant
        
        # Load or create sprite
        asset_path = f'assets/asteroid{variant}.png'
        self.image = load_and_scale_image(asset_path, (size*2, size*2))
        if self.image is None:
            self.image = create_procedural_asteroid(size, variant)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy  # Moving DOWN (we're going UP)
        self.rotation += self.rotation_speed
    
    def draw(self, screen):
        rotated = pygame.transform.rotate(self.image, self.rotation)
        rect = rotated.get_rect(center=(self.x, self.y))
        screen.blit(rotated, rect)
    
    def is_off_screen(self):
        return (self.x < -100 or self.x > SCREEN_WIDTH + 100 or 
                self.y < -100 or self.y > SCREEN_HEIGHT + 100)
    
    def collides_with(self, rocket_x, rocket_y, rocket_size):
        distance = math.sqrt((self.x - rocket_x)**2 + (self.y - rocket_y)**2)
        return distance < (self.size + rocket_size//3)  # More forgiving hitbox

def draw_premium_hud(screen, score, difficulty, font, small_font):
    """Draw modern HUD"""
    # Score panel
    panel = pygame.Surface((250, 80), pygame.SRCALPHA)
    pygame.draw.rect(panel, (10, 10, 30, 180), (0, 0, 250, 80), border_radius=10)
    pygame.draw.rect(panel, NEON_CYAN, (0, 0, 250, 80), 3, border_radius=10)
    
    score_text = font.render(f"SCORE", True, NEON_CYAN)
    score_value = font.render(f"{score}", True, WHITE)
    panel.blit(score_text, (10, 5))
    panel.blit(score_value, (10, 35))
    
    screen.blit(panel, (SCREEN_WIDTH - 270, 20))
    
    # Difficulty bar
    diff_panel = pygame.Surface((200, 50), pygame.SRCALPHA)
    pygame.draw.rect(diff_panel, (10, 10, 30, 180), (0, 0, 200, 50), border_radius=10)
    
    diff_text = small_font.render("DIFFICULTY", True, NEON_PINK)
    diff_panel.blit(diff_text, (10, 5))
    
    # Difficulty bar
    bar_width = 180
    fill_width = int((difficulty / 4) * bar_width)
    pygame.draw.rect(diff_panel, (50, 50, 50), (10, 28, bar_width, 12), border_radius=5)
    pygame.draw.rect(diff_panel, NEON_ORANGE, (10, 28, fill_width, 12), border_radius=5)
    
    screen.blit(diff_panel, (20, 20))

WHITE = (255, 255, 255)