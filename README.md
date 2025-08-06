# SpeedO

**SpeedO** is a terminal-based Internet Speed & Stress Testing tool  
developed by **Dr.Pinnacle (Vishwanath Akuthota © 2025)**.

## Features

- Download, Upload, Ping & Jitter tests  
- Stress test modes:
  - `L` (5 min), `M` (10 min), `H` (15 min), `V` (30 min), `E` (1 hr), `D` (1 day), `Y` (1 year)
  - Or custom duration in seconds (e.g., `-S 5000`)
- Auto-start test after delay (`-r 30`)
- Run specific test only (`-T U`, `-T D`, `-T P`)
- Future: CSV logging & live ASCII speedometer (planned v2)

## Installation

```bash
git clone https://github.com/vishwanathakuthota/speedo.git
cd speedo
pip install -r requirements.txt
```
Ensure speedtest-cli binary is installed:
```
brew install speedtest-cli   # macOS
# or
pip install speedtest-cli
```
## Parameters

|        Flag      |                    Description                   |       Example     |
|:----------------:|:------------------------------------------------:|:-----------------:|
|   -S, --stress   |   Stress mode (L/M/H/V/E/D/Y) or seconds         |   -S M or -S 500  |
|   -T, --test     |   Test type: U (upload), D (download), P (ping)  |   -T D            |
|   -r, --run      |   Auto-start after delay (seconds)               |   -r 30           |
|   -P, --ping     |   Number of ping samples                         |   -P 100          |
|   -O, --timeout  |   Ping timeout in milliseconds                   |   -O 6000         |

## Usage

### Full speed test
```
python3 speedo.py
```
### Run upload only
```
python3 speedo.py -T U
```
### Stress test for 10 minutes
```
python3 speedo.py -S M
```
### Custom stress test (300 seconds)
```
python3 speedo.py -S 300
```

### Auto-start test after 20 seconds
```
python3 speedo.py -r 20
```

## License
This project is licensed under the Custom Dr.Pinnacle License — see LICENSE for details.


