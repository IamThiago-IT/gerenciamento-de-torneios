# Tournament Management System

A C++ application for managing sports tournaments, including player registration, team management, match simulation, and ranking generation.

## Features

- **Player Management** - Register players with name, age, sport, and type (Amateur/Professional)
- **Team Management** - Create teams and assign players
- **Tournament Creation** - Support for different tournament formats:
  - Knockout (Mata-Mata)
  - Round Robin (Pontos Corridos)
- **Match Simulation** - Automatic match result generation
- **Ranking System** - Generate and display final standings
- **Data Persistence** - Export rankings and player data to CSV files

## Project Structure

```
├── coding/
│   └── main.cpp      # Main application source code
├── docs/             # Documentation
├── old/
│   └── main.py       # Legacy Python version
└── README.md
```

## Classes Overview

| Class | Description |
|-------|-------------|
| `Jogador` (Player) | Manages player data and statistics (wins, losses, draws) |
| `Equipe` (Team) | Groups players into teams |
| `Partida` (Match) | Handles match simulation and results |
| `Torneio` (Tournament) | Manages tournament rounds and participants |
| `Ranking` | Generates and exports final standings |
| `Persistencia` | Handles data persistence to files |

## Requirements

- C++11 or higher
- A C++ compiler (g++, clang++, etc.)

## Building & Running

```bash
# Navigate to the coding directory
cd coding

# Compile
g++ -std=c++11 -o tournament main.cpp

# Run
./tournament
```

## Sample Output

```
=== Sistema de Gerenciamento de Torneios ===
Equipe: Time A
 - Ana | V:0 D:0 E:0
 - Carlos | V:0 D:0 E:0
Rodadas geradas com sucesso!
Ana 3 x 2 Carlos

=== Ranking Final ===
Ana - 3 pts
Carlos - 1 pts
Ranking exportado para ranking.csv
```

## Data Export

The system exports data to CSV files:
- `ranking.csv` - Final tournament standings
- `jogadores.csv` - Player statistics

## License

This project is open source and available for educational purposes.