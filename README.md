# Deep Q-Network Agent for Custom PyGame Game

> **Note:** This project is currently under active development. The code and documentation are subject to change as I build out the agent's capabilities.

This repository contains the implementation of a **Deep Q-Network (DQN)** agent designed to learn, play, and master a custom 2D game environment built using **PyGame**.




---

## 🎯 Project Objective

The primary goal of this project is to engineer a **Reinforcement Learning** agent that learns optimal policies entirely through self-play within a custom-built PyGame environment.

This project aims to demonstrate a practical application of Deep Q-Learning by training an agent that can significantly outperform baseline strategies (e.g., a random-action agent) and successfully navigate the game's core mechanics and objectives.

---

## 🧠 Planned Architecture

The DQN agent is built upon the following components:

- **Custom Game Environment (PyGame)**  
  A 2D environment designed from scratch to provide state observations, action space, and reward signals.

- **DQN Agent**  
  Core logic that interfaces between the neural network and the environment. Implements an **epsilon-greedy** policy to balance exploration and exploitation.

- **Neural Network Model (PyTorch)**  
  A deep network that takes the current game state as input and outputs Q-values for each possible action.

- **Experience Replay Buffer**  
  Stores past transitions `(state, action, reward, next_state, done)` and allows training on random batches for better stability.

- **Target Network**  
  A periodically updated copy of the Q-network used to compute stable target Q-values.

- **Reward System**  
  Custom reward shaping to encourage faster and more stable learning in a sparse-reward setting.

---

## 🛣️ Project Roadmap

- [x] Develop and finalize the custom PyGame game environment.
- [ ] Implement the Experience Replay Buffer module (`replay_buffer.py`).
- [ ] Build the DQN neural network model architecture (`model.py`).
- [ ] Develop the core Agent logic connecting all components (`dqn_agent.py`).
- [ ] Create the main training loop to run simulations (`train.py`).
- [ ] Train the agent, tune hyperparameters, and log performance metrics.
- [ ] Benchmark final agent performance against baseline models.
- [ ] Develop a script to watch the trained agent play (`play.py`).

---

## 🧰 Technologies Used

- **Python 3.x**
- **PyTorch** – For building and training the deep Q-network.
- **PyGame** – For creating the custom 2D game environment.
- **NumPy** – For numerical computations and data handling.


---

## 📌 Future Enhancements

- Hyperparameter optimization
- TensorBoard or WandB logging
- Multi-environment training
- Curriculum learning
- Performance visualization and evaluation tools



