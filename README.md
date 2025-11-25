# **🚀 Dual RL Agent Asteroid Avoidance**

**A self-regulating Reinforcement Learning environment where a Pilot Agent learns to survive while a Difficulty Agent learns to optimize the challenge.**

##  Team Members- 

| Name | Roll No. |
| :---- | :---- |
| **Harshit Rana** | 23CSU120 |
| **Harsh Yadav** | 23CSU114 |
| **Harshit** | 23CSU117 |
| **Hardyanshu** | 23CSU113 |

## **📖 Overview**

This project implements a **Dual-Agent Reinforcement Learning system** for a custom Asteroid Dodger game. Unlike traditional RL environments with static difficulty, this system employs two distinct agents that co-adapt:

1. **🚀 Rocket Agent (DQN):** Controls the spaceship, learning optimal evasion maneuvers to maximize survival time.  
2. **🎛️ Difficulty Agent (Tabular Q-Learning):** Dynamically adjusts game parameters (asteroid speed, spawn rate) to maintain an optimal "Flow" state—preventing the game from being too easy (boring) or too hard (frustrating) for the Rocket Agent.

The result is an automated **curriculum learning** system where the environment scales in complexity as the pilot becomes more skilled.

## **🖼️ Gameplay Demo**

*(Place a gameplay GIF or screenshot here)*

*The agent maneuvering through a dense asteroid field using its learned policy.*

## **🧠 Architecture & Training**

### **The Agents**

| Component | Agent Type | Algorithm | Goal |
| :---- | :---- | :---- | :---- |
| **Rocket Pilot** | Deep RL | **DQN** (Deep Q-Network) | Maximize survival time & avoid collisions. |
| **Director** | Tabular RL | **Q-Learning** | Adjust difficulty to keep Pilot performance in target range. |

### **Observation & Action Spaces**

* **State Space (17 inputs):** Rocket position (x, y), relative distances, angles, and speeds of the 5 nearest asteroids.  
* **Action Space (5 actions):** Idle, Thrust Up, Thrust Down, Rotate Left, Rotate Right.  
* **Reward Function:** Positive reward for every frame alive; negative penalties for hugging walls; large negative penalty for collision.

## **📊 Performance Results**

Training over 1000+ episodes demonstrates a clear transition from random exploration to stable exploitation.

| Training Phase | Exploration (ϵ) | Avg Score | Behavior Observed |
| :---- | :---- | :---- | :---- |
| **Early (Ep 200\)** | High (\~0.37) | \~610 | High variance, erratic movement, frequent crashes. |
| **Mid (Ep 600\)** | Low (\~0.05) | \~900 | Learning safe zones, but struggles with high-speed clusters. |
| **Final (Ep 1000+)** | Minimal (0.01) | **\~2100** | **Stable Policy:** Efficient dodging, maximized survival time. |

## **📂 Project Structure**

Asteroid\_Dodger\_RL/  
├── main.py                 \# Entry point: Training loop & Game execution  
├── game\_env.py             \# Custom Gym-style Pygame environment  
├── rocket\_agent.py         \# DQN Agent (Neural Network architecture)  
├── difficulty\_agent.py     \# Q-Table Agent (Adaptive difficulty logic)  
├── utils.py                \# Assets, colors, and particle systems  
├── requirements.txt        \# Python dependencies  
├── assets/                 \# Sprites and images  
└── rocket\_model\_final.pth  \# The best trained model weights

## **🎮 Installation & Usage**

### **1\. Prerequisites**

Ensure you have Python installed. Clone the repository and install dependencies:

git clone https://github.com/harshiit-rana/Dual-RL-Agent-in-Asteroid-Dodger-Game
cd asteroid-dodger-rl  
pip install \-r requirements.txt

### **2\. Running the Project**

Execute the main script to access the menu:

python main.py

You will be presented with three modes:

1. **Train RL Agents:** Starts the training loop (headless or rendered).  
2. **Watch Trained Agent:** Loads rocket\_model\_final.pth and visualizes the result.  
3. **Play Manually:** You control the rocket using Arrow Keys, but the **Difficulty Agent** still runs in the background, adapting the game to your skill level\!

## **⚙️ Configuration**

To retrain the model from scratch or adjust hyperparameters, modify the constants in main.py or rocket\_agent.py:

\# Example: rocket\_agent.py  
self.learning\_rate \= 0.0005  
self.gamma \= 0.99  
self.epsilon\_decay \= 0.995

To run training:

python main.py  
\# Select Option 1  
