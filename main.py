import pygame
import numpy as np
from game_env import AsteroidDodgerEnv
from rocket_agent import RocketAgent
from difficulty_agent import DifficultyAgent
import os
import time

# Create assets folder if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

def train_mode(episodes=2000, render=False):
    env = AsteroidDodgerEnv(render_mode=render)
    rocket_agent = RocketAgent(state_size=17, action_size=5)
    difficulty_agent = DifficultyAgent()
    
    scores = []
    
    # Fixed difficulty during training to let agent learn stable dynamics
    fixed_diff = 1
    diff_params = difficulty_agent.get_difficulty_params(fixed_diff)
    env.set_difficulty(diff_params['spawn_rate'], diff_params['speed'])
    env.difficulty_level = fixed_diff + 1
    
    for episode in range(episodes):
        state = env.reset()
        done = False
        episode_reward = 0
        
        step_count = 0
        
        # auto-save filenames
        save_every = 200
        
        while not done:
            # don't pump pygame events if render=False (but still allow quit when render True)
            if render:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        env.close()
                        return
            
            action = rocket_agent.act(state)
            next_state, reward, done, _ = env.step(action)
            
            rocket_agent.remember(state, action, reward, next_state, done)
            state = next_state
            episode_reward += reward
            
            step_count += 1
            
            # replay every N steps for faster learning
            if step_count % 4 == 0:
                rocket_agent.replay(batch_size=64)
            
            if render:
                env.render()
        
        # end episode
        rocket_agent.replay(batch_size=128)  # a final replay
        scores.append(env.score)
        avg_score = np.mean(scores[-100:])
        
        print(f"Episode {episode+1}/{episodes} | Score: {env.score} | Avg100: {avg_score:.2f} | Eps: {rocket_agent.epsilon:.3f}")
        
        # autosave
        if (episode + 1) % save_every == 0:
            fname = f"rocket_model_ep{episode+1}.pth"
            rocket_agent.save(fname)
            print(f"💾 Saved {fname}")
    
    # final save
    rocket_agent.save("rocket_model_final.pth")
    print("Training finished. Model saved as rocket_model_final.pth")
    env.close()

def play_mode():
    env = AsteroidDodgerEnv(render_mode=True)
    rocket_agent = RocketAgent(state_size=17, action_size=5)
    
    model_loaded = False
    if os.path.exists("rocket_model_final.pth"):
        try:
            rocket_agent.load("rocket_model_final.pth")
            model_loaded = True
            print("✅ Loaded rocket_model_final.pth")
        except Exception as e:
            print("⚠️ Failed loading model:", e)
    
    if not model_loaded:
        saved = [f for f in os.listdir('.') if f.startswith('rocket_model_ep') and f.endswith('.pth')]
        if saved:
            saved.sort()
            rocket_agent.load(saved[-1])
            print("✅ Loaded", saved[-1])
    
    difficulty_agent = DifficultyAgent()
    # now enable adaptive difficulty while playing
    perf_state = 2
    diff_action = 1
    diff_params = difficulty_agent.get_difficulty_params(diff_action)
    env.set_difficulty(diff_params['spawn_rate'], diff_params['speed'])
    env.difficulty_level = diff_action + 1
    
    state = env.reset()
    done = False
    step_count = 0
    previous_score = 0
    
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        
        action = rocket_agent.act(state)
        state, reward, done, _ = env.step(action)
        env.render()
        
        step_count += 1
        if step_count % 300 == 0:
            current_perf_state = difficulty_agent.get_performance_state(env.score, env.time_alive)
            diff_reward = difficulty_agent.calculate_reward(env.score, env.time_alive, previous_score)
            difficulty_agent.update(perf_state, diff_action, diff_reward, current_perf_state)
            perf_state = current_perf_state
            diff_action = difficulty_agent.choose_action(perf_state)
            diff_params = difficulty_agent.get_difficulty_params(diff_action)
            env.set_difficulty(diff_params['spawn_rate'], diff_params['speed'])
            env.difficulty_level = diff_action + 1
            previous_score = env.score
    
    env.show_game_over()
    print(f"🏆 Final Score: {env.score}")
    env.close()

def manual_play_mode():
    env = AsteroidDodgerEnv(render_mode=True)
    difficulty_agent = DifficultyAgent()
    
    state = env.reset()
    done = False
    
    print("\n🎮 Controls: Arrow Keys = Move | ESC = Quit\n")
    
    while not done:
        action = 0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            action = 1
        elif keys[pygame.K_DOWN]:
            action = 2
        elif keys[pygame.K_LEFT]:
            action = 3
        elif keys[pygame.K_RIGHT]:
            action = 4
        
        state, reward, done, _ = env.step(action)
        env.render()
    
    env.show_game_over()
    print(f"\n🏆 Game Over! Final Score: {env.score}")
    env.close()

if __name__ == "__main__":
    print("=" * 60)
    print("  🚀 ASTEROID DODGER - PREMIUM RL EDITION 🚀")
    print("=" * 60)
    print("\n1. Train RL Agents")
    print("2. Watch Trained Agent Play")
    print("3. Play Manually (with RL difficulty)\n")
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice == "1":
        eps = int(input("Episodes (default 2000): ") or "2000")
        headless = input("Render while training? (y/N): ").strip().lower() == 'y'
        train_mode(episodes=eps, render=headless)
    elif choice == "2":
        play_mode()
    elif choice == "3":
        manual_play_mode()
    else:
        print("Invalid choice!")
