import pygame
import numpy as np
import random
import math
from utils import *

class AsteroidDodgerEnv:
    def __init__(self, render_mode=True):
        self.render_mode = render_mode
        self.rocket = Rocket()
        self.asteroids = []
        self.score = 0
        self.time_alive = 0
        self.difficulty_level = 1
        
        # Difficulty parameters (defaults)
        self.spawn_rate = 0.02
        self.asteroid_speed_multiplier = 1.0
        
        if self.render_mode:
            pygame.init()
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption("🚀 Asteroid Dodger RL - Premium Edition")
            self.clock = pygame.time.Clock()
            
            # Fonts
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
            self.big_font = pygame.font.Font(None, 72)
            
            # Background elements
            self.stars = StarField()
            self.nebula = NebulaClouds()
            self.explosion_particles = ParticleSystem()
    
    def reset(self):
        self.rocket = Rocket()
        self.asteroids = []
        self.score = 0
        self.time_alive = 0
        if self.render_mode:
            self.explosion_particles = ParticleSystem()
        return self._get_state()
    
    def _get_state(self):
        """State for RL agent"""
        rocket_x = self.rocket.x / SCREEN_WIDTH
        rocket_y = self.rocket.y / SCREEN_HEIGHT
        
        distances = []
        angles = []
        speeds = []
        
        for ast in self.asteroids:
            dx = ast.x - self.rocket.x
            dy = ast.y - self.rocket.y
            dist = math.sqrt(dx**2 + dy**2)
            distances.append(dist)
            angles.append(math.atan2(dy, dx))
            speeds.append(math.sqrt(ast.vx**2 + ast.vy**2))
        
        if len(distances) >= 5:
            indices = np.argsort(distances)[:5]
            nearest_dists = [distances[i] / 1000 for i in indices]
            nearest_angles = [angles[i] / math.pi for i in indices]
            nearest_speeds = [speeds[i] / 10 for i in indices]
        else:
            nearest_dists = (distances + [1000.0] * 5)[:5]
            nearest_angles = (angles + [0.0] * 5)[:5]
            nearest_speeds = (speeds + [0.0] * 5)[:5]
        
        state = [rocket_x, rocket_y] + nearest_dists + nearest_angles + nearest_speeds
        return np.array(state, dtype=np.float32)
    
    def step(self, action):
        # action: 0=nothing, 1=up, 2=down, 3=left, 4=right
        self.rocket.update(action)
        self.time_alive += 1
        
        # Spawn asteroids
        if random.random() < self.spawn_rate:
            self._spawn_asteroid()
        
        for ast in self.asteroids:
            ast.update()
        
        # Cull off-screen asteroids
        self.asteroids = [ast for ast in self.asteroids if not ast.is_off_screen()]
        
        done = False
        # base reward for surviving this step (encourage survival)
        reward = 0.15
        
        # small reward shaping: encourage moving up (progress) and staying away from walls
        if action == 1:
            reward += 0.05  # encourage upwards movement (dodging)
        if self.rocket.x < 70 or self.rocket.x > SCREEN_WIDTH - 70:
            reward -= 0.08  # discourage hugging vertical edges
        if self.rocket.y < 70:
            # discourage hugging top too close (since asteroids spawn above screen they may pass)
            reward -= 0.03
        
        # extra shaping: distance to nearest asteroid
        if self.asteroids:
            dists = [math.hypot(ast.x - self.rocket.x, ast.y - self.rocket.y) for ast in self.asteroids]
            min_dist = min(dists)
            # closer -> negative small penalty, far -> small bonus
            reward += max(-0.2, min(0.2, (min_dist - 100) / 400.0))
        else:
            reward += 0.02
        
        for ast in self.asteroids:
            if ast.collides_with(self.rocket.x, self.rocket.y, self.rocket.size):
                done = True
                reward = -100.0
                if self.render_mode:
                    self.explosion_particles.emit(self.rocket.x, self.rocket.y, NEON_ORANGE, 30, (2, 5))
                break
        
        if not done:
            self.score += 1
        
        return self._get_state(), reward, done, {}
    
    def _spawn_asteroid(self):
        """Spawn from TOP, moving DOWN (mostly)"""
        x = random.randint(50, SCREEN_WIDTH - 50)
        y = -50  # Spawn above screen
        
        # Velocity: mostly downward, with some horizontal
        vx = random.uniform(-1.5, 1.5) * self.asteroid_speed_multiplier
        vy = random.uniform(2.5, 4.5) * self.asteroid_speed_multiplier  # DOWN
        
        size = random.randint(18, 45)
        variant = random.randint(1, 3)
        
        self.asteroids.append(Asteroid(x, y, vx, vy, size, variant))
    
    def set_difficulty(self, spawn_rate, speed_multiplier):
        self.spawn_rate = spawn_rate
        self.asteroid_speed_multiplier = speed_multiplier
    
    def render(self):
        if not self.render_mode:
            return
        
        # Background gradient
        for y in range(SCREEN_HEIGHT):
            color_val = int(5 + (y / SCREEN_HEIGHT) * 10)
            pygame.draw.line(self.screen, (color_val, color_val, color_val + 20), 
                           (0, y), (SCREEN_WIDTH, y))
        
        # Nebula clouds & stars
        self.nebula.update()
        self.nebula.draw(self.screen)
        self.stars.update()
        self.stars.draw(self.screen)
        
        for ast in self.asteroids:
            ast.draw(self.screen)
        
        self.rocket.draw(self.screen)
        
        # Explosion particles
        self.explosion_particles.update()
        self.explosion_particles.draw(self.screen)
        
        # HUD
        draw_premium_hud(self.screen, self.score, self.difficulty_level, 
                        self.font, self.small_font)
        
        pygame.display.flip()
        self.clock.tick(FPS)
    
    def show_game_over(self):
        if not self.render_mode:
            return
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.big_font.render("GAME OVER", True, NEON_PINK)
        score_text = self.font.render(f"Final Score: {self.score}", True, NEON_CYAN)
        
        self.screen.blit(game_over_text, 
                        (SCREEN_WIDTH//2 - game_over_text.get_width()//2, 
                         SCREEN_HEIGHT//2 - 50))
        self.screen.blit(score_text, 
                        (SCREEN_WIDTH//2 - score_text.get_width()//2, 
                         SCREEN_HEIGHT//2 + 30))
        
        pygame.display.flip()
        pygame.time.wait(1000)
    
    def close(self):
        if self.render_mode:
            pygame.quit()
