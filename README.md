# 🎮 Cheza - Premium Tetris Experience

<div align="center">

![Cheza Logo](https://img.shields.io/badge/CHEZA-Tetris%20Game-blue?style=for-the-badge&logo=gamepad)

**A modern, feature-rich Tetris implementation with dynamic resizing and premium gameplay**

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg?style=flat-square&logo=python)](https://python.org)
[![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg?style=flat-square)](https://pygame.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Stars](https://img.shields.io/github/stars/llakterian/Cheza?style=flat-square)](https://github.com/llakterian/Cheza/stargazers)

[🎯 Features](#-features) • [🚀 Quick Start](#-quick-start) • [🎮 Controls](#-controls) • [📸 Screenshots](#-screenshots) • [💰 Commercial Use](#-commercial-licensing)

</div>

---

## ✨ Features

### 🎨 **Visual Excellence**
- **Stunning Graphics**: Crisp, colorful blocks with smooth animations
- **Dynamic Resizing**: Responsive game board that adapts to any window size
- **Modern UI**: Clean, intuitive interface with real-time statistics
- **Professional Design**: Carefully crafted color scheme and typography

### 🎯 **Gameplay Features**
- **Classic Tetris Mechanics**: All 7 standard Tetrimino pieces (I, J, L, O, S, T, Z)
- **Advanced Controls**: 
  - Piece rotation and movement
  - Hard drop for instant placement
  - Hold system for strategic piece management
  - Soft drop with scoring bonus
- **Progressive Difficulty**: Speed increases with level progression
- **Smart Scoring System**: Bonus points for line clears, drops, and combos
- **Pause & Resume**: Full game state preservation

### 🔧 **Technical Excellence**
- **Optimized Performance**: Smooth 60 FPS gameplay
- **Responsive Design**: Intelligent UI scaling and repositioning
- **Size Constraints**: Configurable block sizes (20px - 50px)
- **Memory Efficient**: Lightweight codebase with minimal resource usage

---

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Installation

#### Option 1: Automated Setup (Recommended)
```bash
git clone https://github.com/llakterian/Cheza.git
cd Cheza
chmod +x install.sh launch_cheza.sh
./install.sh
./launch_cheza.sh
```

#### Option 2: Manual Installation
```bash
git clone https://github.com/llakterian/Cheza.git
cd Cheza
pip install pygame
python cheza.py
```

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| `←` `→` | Move piece left/right |
| `↓` | Soft drop (bonus points) |
| `↑` | Rotate piece clockwise |
| `Space` | Hard drop (instant placement) |
| `C` | Hold current piece |
| `P` | Pause/Resume game |
| `R` | Restart game |
| **Mouse** | Resize window by dragging edges |

---

## 📸 Screenshots

<div align="center">

### 🎯 Gameplay
*Experience smooth, responsive Tetris action*

### 🎨 Dynamic Resizing
*Resize your game window - everything scales perfectly*

### 📊 Statistics Tracking
*Real-time score, level, and line tracking*

</div>

---

## 🏗️ Architecture

### Core Components
- **`TetrisGame`**: Main game engine and state management
- **`Tetrimino`**: Piece logic, rotation, and collision detection
- **Dynamic Rendering**: Responsive UI system
- **Event Handling**: Smooth input processing

### Key Features Implementation
- **Collision Detection**: Precise boundary and piece overlap checking
- **Line Clearing**: Efficient row completion detection and removal
- **Scoring System**: Multi-factor scoring with level progression
- **Hold System**: Strategic piece management with swap limitations

---

## 🎯 Game Mechanics

### Scoring System
| Action | Points |
|--------|--------|
| Single Line | 40 × Level |
| Double Lines | 100 × Level |
| Triple Lines | 300 × Level |
| Tetris (4 lines) | 500 × Level |
| Soft Drop | 0.5 per cell |
| Hard Drop | 1 per cell |

### Level Progression
- **Level Up**: Every 10 lines cleared
- **Speed Increase**: Faster piece falling with each level
- **Dynamic Difficulty**: Adaptive challenge scaling

---

## 💰 Commercial Licensing

**Cheza** is available for commercial use and distribution. Perfect for:
- 🎮 Game development portfolios
- 🏢 Educational institutions
- 🎯 Entertainment venues
- 📱 Mobile game inspiration
- 🎨 UI/UX design reference

### Business Features
- Clean, maintainable codebase
- Comprehensive documentation
- Scalable architecture
- Cross-platform compatibility
- Professional presentation ready

---

## 🛠️ Development

### System Requirements
- **OS**: Windows, macOS, Linux
- **Python**: 3.7+
- **RAM**: 50MB minimum
- **Storage**: 10MB

### Customization Options
- Adjustable grid dimensions
- Customizable color schemes
- Configurable scoring systems
- Modifiable piece shapes
- Flexible UI layouts

---

## 📞 Contact & Support

<div align="center">

### 👨‍💻 Developer: **@llakterian**

[![Email](https://img.shields.io/badge/Email-llakterian@gmail.com-red?style=for-the-badge&logo=gmail)](mailto:llakterian@gmail.com)
[![Twitter](https://img.shields.io/badge/Twitter-@llakterian-blue?style=for-the-badge&logo=twitter)](https://twitter.com/llakterian)
[![Discord](https://img.shields.io/badge/Discord-@llakterian-purple?style=for-the-badge&logo=discord)](https://discord.com/users/llakterian)

**💼 Available for custom development, licensing, and commercial partnerships**

</div>

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

### 🌟 **Star this repository if you found it helpful!** 🌟

**Built with ❤️ by [@llakterian](https://github.com/llakterian)**

*Ready to play? Clone, install, and enjoy the ultimate Tetris experience!*

</div>
