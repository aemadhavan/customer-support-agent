#!/usr/bin/env python3
"""
Database reset script for Assignment 4: Customer Support.
Satisfies Stage 1 reset requirement and SPEC M-1.
Performs clean-slate reset via Docker container volume lifecycle (Option B).
"""

import subprocess
import sys
import time

def reset_docker_db() -> int:
    print("Resetting database via Docker volume teardown (Option B)...")
    
    # 1. Teardown container and destroy volume
    down_cmd = ["docker", "compose", "down", "-v"]
    print(f"Running: {' '.join(down_cmd)}")
    subprocess.run(down_cmd, check=True)
    
    # 2. Re-create and start postgres container with clean volume
    up_cmd = ["docker", "compose", "up", "-d", "postgres"]
    print(f"Running: {' '.join(up_cmd)}")
    subprocess.run(up_cmd, check=True)
    
    # 3. Wait for PostgreSQL to become healthy and finish init script
    print("Waiting for PostgreSQL to complete initialization...")
    max_wait_seconds = 30
    start_time = time.time()
    
    while time.time() - start_time < max_wait_seconds:
        result = subprocess.run(
            ["docker", "exec", "cs_postgres", "pg_isready", "-U", "postgres", "-d", "customer_support"],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("PostgreSQL is ready and seeded successfully!")
            return 0
        time.sleep(1)
        
    print("Error: PostgreSQL failed to become ready in time.", file=sys.stderr)
    return 1

if __name__ == "__main__":
    sys.exit(reset_docker_db())
