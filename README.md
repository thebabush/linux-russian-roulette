# Linux Russian Roulette

Take a random PoC from [syzbot](https://syzkaller.appspot.com/upstream) and run it on your system for maximum fun!

Also known as _crash-all-the-things.py_

## How it works

1. Download a testcase from syzbot (basically, 0-days)
2. Compile it
3. (Optional) run it

## What it does

- Crash your machines
- Crash your VMs
- Crash your machines from your VMs
- Crash a system from docker

## Warning

Don't run this.
Your are basically throwing random DoS exploits to your kernel.
Typically, a kernel does not like that.

I repeat, do not run this.

## Usage

To just compile random C testcases:

```sh
./linux-russian-roulette.py
```

If you are crazy enough to actually run the programs:

```sh
./linux-russian-roulette.py whatever
```

## Now with Docker! 

For even more dangerous fun, you can run this in a Docker container! 

```sh
# Build the container
docker compose build

# Run compilation only (safer, non-privileged)
docker compose run roulette

# Run with execution (requires privileged mode - EXTREMELY DANGEROUS)
ROULETTE_PRIVILEGED=true docker compose run roulette python3 linux-russian-roulette.py go
```

The `ROULETTE_PRIVILEGED=true` flag enables privileged mode, which gives the container full access to your host system.

## Why

- Why not?
- Annoy CTF organizers
- Annoy your cloud provider
- Be arrested
