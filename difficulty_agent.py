import numpy as np
import random

class DifficultyAgent:
    def __init__(self):
        self.num_actions = 4
        # small q-table, but this will not be used to randomly flip difficulty during training in main
        self.q_table = np.zeros((10, self.num_actions))
        self.learning_rate = 0.1
        self.gamma = 0.9
        self.epsilon = 0.2  # low exploration by default
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.995
        
        # difficulty presets: (spawn_rate, speed)
        self.difficulty_params = {
            0: {'spawn_rate': 0.01, 'speed': 0.8},
            1: {'spawn_rate': 0.02, 'speed': 1.0},
            2: {'spawn_rate': 0.03, 'speed': 1.3},
            3: {'spawn_rate': 0.05, 'speed': 1.6}
        }
    
    def get_performance_state(self, score, time_alive):
        performance = score / max(time_alive, 1)
        if performance < 0.3: return 0
        elif performance < 0.5: return 1
        elif performance < 0.7: return 2
        elif performance < 0.85: return 3
        else: return 4  # cap state
    
    def choose_action(self, state):
        if random.random() < self.epsilon:
            return random.randint(0, self.num_actions - 1)
        return np.argmax(self.q_table[state % self.q_table.shape[0]])
    
    def update(self, state, action, reward, next_state):
        best_next_action = np.argmax(self.q_table[next_state % self.q_table.shape[0]])
        td_target = reward + self.gamma * self.q_table[next_state % self.q_table.shape[0]][best_next_action]
        td_error = td_target - self.q_table[state % self.q_table.shape[0]][action]
        self.q_table[state % self.q_table.shape[0]][action] += self.learning_rate * td_error
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
    
    def get_difficulty_params(self, action):
        return self.difficulty_params[action % len(self.difficulty_params)]
    
    def calculate_reward(self, score, time_alive, previous_score):
        performance = score / max(time_alive, 1)
        score_increase = score - previous_score
        
        if 0.6 < performance < 0.9 and score_increase > 0:
            return 5
        elif performance > 0.95:
            return -3
        elif performance < 0.3:
            return -3
        else:
            return 0
