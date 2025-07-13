# AGENTS.md

## Project Overview
Linux Russian Roulette - A tool that downloads and compiles kernel exploits from syzkaller for educational/testing purposes.

## Key Files
- `linux-russian-roulette.py` - Main script that downloads and compiles kernel exploits
- `Dockerfile` - Ubuntu container with build tools
- `docker-compose.yml` - Container orchestration with privileged access

## Architecture
- Downloads exploit code from syzkaller.appspot.com
- Creates temporary directories for compilation and execution
- Compiles exploits with GCC
- Optionally runs compiled exploits with timeout

## Safety Notes
- Script uses temporary directories that auto-cleanup
- Docker container provides isolation
- Privileged mode required for kernel-level exploits
- Educational/research tool only