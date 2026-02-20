#!/usr/bin/env python3
"""
Demo: Ralph Loop with Sound Notifications

This demo shows how the Ralph Loop plays different sounds:
- Tink (subtle): When iterations are incomplete
- Hero (success): When task completes successfully  
- Funk (warning): When hitting iteration/token/cost limits
- Basso (error): When errors occur
"""

import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from ralph_loop_agent import RalphLoopAgent, RalphLoopConfig
import time


def demo_successful_completion():
    """Demo: Successful task completion with sounds"""
    print("\n" + "="*70)
    print("DEMO 1: Successful Task Completion")
    print("="*70)
    print("\nYou should hear:")
    print("  🔔 Tink (subtle) - 2 times for incomplete iterations")
    print("  🎉 Hero (triumphant) - When task completes")
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    config = RalphLoopConfig(
        agent_type='docs',
        max_iterations=5,
        verbose=True,
        enable_sounds=True
    )
    
    ralph = RalphLoopAgent(config)
    
    def mock_success(prompt, context, iteration):
        if iteration <= 2:
            return {'text': 'Incomplete output'}
        else:
            return {
                'text': '''# Overview
Complete documentation.

## Quick Start
Getting started.

## API Reference
API docs.

## Examples
Examples here.

## Configuration
Config options.

Documentation complete.
'''
            }
    
    result = ralph.execute_loop('Write docs', {}, mock_success)
    print(f"\n✅ Result: {result.completion_reason}\n")


def demo_max_iterations():
    """Demo: Hitting max iterations limit"""
    print("\n" + "="*70)
    print("DEMO 2: Max Iterations Reached")
    print("="*70)
    print("\nYou should hear:")
    print("  🔔 Tink (subtle) - 3 times for incomplete iterations")
    print("  ⚠️  Funk (warning) - When max iterations hit")
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    config = RalphLoopConfig(
        agent_type='docs',
        max_iterations=3,
        verbose=True,
        enable_sounds=True
    )
    
    ralph = RalphLoopAgent(config)
    
    def mock_incomplete(prompt, context, iteration):
        # Always return incomplete output
        return {'text': 'Still incomplete...'}
    
    result = ralph.execute_loop('Write docs', {}, mock_incomplete)
    print(f"\n⚠️  Result: {result.completion_reason}\n")


def demo_error():
    """Demo: Error during execution"""
    print("\n" + "="*70)
    print("DEMO 3: Error Handling")
    print("="*70)
    print("\nYou should hear:")
    print("  ❌ Basso (error) - When error occurs")
    print("\nStarting in 2 seconds...")
    time.sleep(2)
    
    config = RalphLoopConfig(
        agent_type='docs',
        max_iterations=5,
        verbose=True,
        enable_sounds=True
    )
    
    ralph = RalphLoopAgent(config)
    
    def mock_error(prompt, context, iteration):
        if iteration == 2:
            raise Exception("Simulated error!")
        return {'text': 'Output before error'}
    
    result = ralph.execute_loop('Write docs', {}, mock_error)
    print(f"\n❌ Result: {result.completion_reason}\n")


def main():
    """Run all demos"""
    print("\n" + "="*70)
    print("🔊 Ralph Loop Sound Notifications Demo")
    print("="*70)
    print("\nThis demo will play different sounds for different events.")
    print("Make sure your volume is at a comfortable level!")
    
    demos = [
        ("Successful Completion", demo_successful_completion),
        ("Max Iterations Warning", demo_max_iterations),
        ("Error Handling", demo_error),
    ]
    
    for i, (name, demo_func) in enumerate(demos, 1):
        print(f"\n\n{'='*70}")
        print(f"Running Demo {i}/{len(demos)}: {name}")
        print('='*70)
        
        try:
            demo_func()
        except Exception as e:
            print(f"\n❌ Demo failed: {e}")
        
        if i < len(demos):
            print("\nPress Enter to continue to next demo...")
            input()
    
    print("\n" + "="*70)
    print("✅ All demos complete!")
    print("="*70)
    print("\nSound Summary:")
    print("  🔔 Tink - Subtle iteration sound (attention may be needed)")
    print("  🎉 Hero - Task completed successfully")
    print("  ⚠️  Funk - Warning (limits reached)")
    print("  ❌ Basso - Error occurred")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
