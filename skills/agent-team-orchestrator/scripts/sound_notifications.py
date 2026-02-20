#!/usr/bin/env python3
"""
Sound Notifications for Agent Team Orchestrator

Plays audio alerts when tasks complete or attention is needed.
"""

import subprocess
import sys
from enum import Enum
from pathlib import Path
from typing import Optional


class NotificationType(Enum):
    """Types of notifications with associated sounds"""
    TASK_COMPLETE = "Glass"      # Task successfully completed
    ATTENTION_NEEDED = "Ping"    # User input or attention required
    ERROR = "Basso"              # Error or failure occurred
    SUCCESS = "Hero"             # Major milestone achieved
    WARNING = "Funk"             # Warning or issue detected
    ITERATION = "Tink"           # Loop iteration completed (subtle)


class SoundNotifier:
    """Handles playing sound notifications"""
    
    def __init__(self, enabled: bool = True, sound_dir: str = "/System/Library/Sounds"):
        """
        Initialize the sound notifier.
        
        Args:
            enabled: Whether sound notifications are enabled
            sound_dir: Directory containing sound files
        """
        self.enabled = enabled
        self.sound_dir = Path(sound_dir)
        self._verify_sounds()
    
    def _verify_sounds(self):
        """Verify that the sound directory exists"""
        if not self.sound_dir.exists():
            print(f"Warning: Sound directory not found: {self.sound_dir}", file=sys.stderr)
            self.enabled = False
    
    def play(self, notification_type: NotificationType, async_play: bool = True):
        """
        Play a notification sound.
        
        Args:
            notification_type: Type of notification to play
            async_play: If True, play sound asynchronously (non-blocking)
        """
        if not self.enabled:
            return
        
        sound_file = self.sound_dir / f"{notification_type.value}.aiff"
        
        if not sound_file.exists():
            print(f"Warning: Sound file not found: {sound_file}", file=sys.stderr)
            return
        
        try:
            if async_play:
                # Non-blocking: play in background
                subprocess.Popen(
                    ["afplay", str(sound_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                # Blocking: wait for sound to finish
                subprocess.run(
                    ["afplay", str(sound_file)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    check=True
                )
        except Exception as e:
            print(f"Warning: Failed to play sound: {e}", file=sys.stderr)
    
    def play_completion(self):
        """Play task completion sound"""
        self.play(NotificationType.TASK_COMPLETE)
    
    def play_attention_needed(self):
        """Play attention needed sound"""
        self.play(NotificationType.ATTENTION_NEEDED)
    
    def play_error(self):
        """Play error sound"""
        self.play(NotificationType.ERROR)
    
    def play_success(self):
        """Play success sound"""
        self.play(NotificationType.SUCCESS)
    
    def play_warning(self):
        """Play warning sound"""
        self.play(NotificationType.WARNING)
    
    def play_iteration(self):
        """Play iteration sound (subtle)"""
        self.play(NotificationType.ITERATION)
    
    def enable(self):
        """Enable sound notifications"""
        self.enabled = True
    
    def disable(self):
        """Disable sound notifications"""
        self.enabled = False
    
    def test_all_sounds(self):
        """Test all notification sounds"""
        print("Testing all notification sounds...\n")
        
        for notification_type in NotificationType:
            print(f"Playing: {notification_type.name} ({notification_type.value})")
            self.play(notification_type, async_play=False)
            print(f"  ✓ {notification_type.name} played\n")


# Global singleton instance
_global_notifier: Optional[SoundNotifier] = None


def get_notifier(enabled: bool = True) -> SoundNotifier:
    """Get or create the global sound notifier instance"""
    global _global_notifier
    
    if _global_notifier is None:
        _global_notifier = SoundNotifier(enabled=enabled)
    
    return _global_notifier


def play_task_complete():
    """Convenience function: play task completion sound"""
    get_notifier().play_completion()


def play_attention_needed():
    """Convenience function: play attention needed sound"""
    get_notifier().play_attention_needed()


def play_error():
    """Convenience function: play error sound"""
    get_notifier().play_error()


def play_success():
    """Convenience function: play success sound"""
    get_notifier().play_success()


def play_warning():
    """Convenience function: play warning sound"""
    get_notifier().play_warning()


# CLI for testing
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test sound notifications")
    parser.add_argument(
        "notification",
        nargs="?",
        choices=[t.name.lower() for t in NotificationType],
        help="Notification type to play"
    )
    parser.add_argument(
        "--test-all",
        action="store_true",
        help="Test all notification sounds"
    )
    parser.add_argument(
        "--disable",
        action="store_true",
        help="Disable sound notifications"
    )
    
    args = parser.parse_args()
    
    notifier = get_notifier(enabled=not args.disable)
    
    if args.test_all:
        notifier.test_all_sounds()
    elif args.notification:
        # Find the notification type
        notification_type = NotificationType[args.notification.upper()]
        print(f"Playing: {notification_type.name}")
        notifier.play(notification_type, async_play=False)
        print("✓ Done")
    else:
        # Default: show available sounds
        print("Available notification sounds:")
        print()
        for notification_type in NotificationType:
            print(f"  {notification_type.name.lower():20} - {notification_type.value}")
        print()
        print("Usage:")
        print(f"  python {sys.argv[0]} <notification>")
        print(f"  python {sys.argv[0]} --test-all")
