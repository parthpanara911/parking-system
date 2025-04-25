#!/usr/bin/env python
"""
Script to clean up the database schema and update demo locations
"""
import os
import subprocess
import sys
import time

def run_command(command, interactive=False):
    """Run a shell command and print the output"""
    print(f"Running: {command}")
    
    if interactive:
        # Run interactively to allow user input
        process = subprocess.Popen(
            command, 
            shell=True, 
            stdin=subprocess.PIPE if not interactive else None
        )
        process.wait()
        if process.returncode != 0:
            print(f"Command failed with exit code {process.returncode}", file=sys.stderr)
            return False
    else:
        # Run with captured output
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.stdout:
            print(result.stdout)
        
        if result.stderr:
            print(f"Error: {result.stderr}", file=sys.stderr)
        
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}", file=sys.stderr)
            return False
    
    return True

def main():
    """Main function to run the cleanup and update operations"""
    print("=" * 60)
    print("Smart Parking System - Database Cleanup and Demo Update")
    print("=" * 60)
    print("\nThis script will:")
    print("1. Run database migrations to remove unused tables and columns")
    print("2. Update 6 specified parking locations for UI demo purposes")
    print("=" * 60)
    
    # Ask for confirmation
    confirm = input("\nDo you want to continue? [y/N]: ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        return
    
    print("\nStep 1: Running database migration...")
    if not run_command("flask db upgrade"):
        print("Migration failed. Stopping.")
        return
    
    print("\nStep 2: Updating demo locations (interactive)...")
    # Run the update script in interactive mode to handle missing locations
    if not run_command("python scripts/update_demo_locations.py", interactive=True):
        print("Update demo locations failed.")
        return
    
    print("\n" + "=" * 60)
    print("SUCCESS: Database schema cleanup and demo location update completed!")
    print("=" * 60)

if __name__ == "__main__":
    main() 