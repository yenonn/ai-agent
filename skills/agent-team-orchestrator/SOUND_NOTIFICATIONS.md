# Sound Notifications

The Agent Team Orchestrator includes audio notifications to alert you when tasks complete or attention is needed.

## Overview

Sound notifications play at key moments during agent execution:

- **🔔 Tink** (subtle) - Plays after each incomplete iteration, signaling that the agent is still working
- **🎉 Hero** (triumphant) - Plays when a task completes successfully
- **⚠️ Funk** (warning) - Plays when limits are reached (max iterations, tokens, or cost)
- **❌ Basso** (error) - Plays when an error occurs

## Usage

### Ralph Loop Integration

Sound notifications are enabled by default in the Ralph Loop:

```python
from ralph_loop_agent import RalphLoopAgent, RalphLoopConfig

config = RalphLoopConfig(
    agent_type='coder',
    max_iterations=10,
    verbose=True,
    enable_sounds=True  # Enabled by default
)

ralph = RalphLoopAgent(config)
result = ralph.execute_loop(task_prompt, context, execute_fn)
```

### Disabling Sounds

You can disable sounds in two ways:

**1. Via Config:**
```python
config = RalphLoopConfig(
    agent_type='coder',
    enable_sounds=False  # Disable sounds
)
```

**2. Via CLI:**
```bash
python ralph_loop_agent.py coder "Implement feature" --no-sounds
```

### Standalone Usage

You can also use the sound notification system independently:

```python
from sound_notifications import get_notifier, NotificationType

# Get the global notifier
notifier = get_notifier(enabled=True)

# Play specific sounds
notifier.play_completion()        # Task complete
notifier.play_attention_needed()  # Attention needed
notifier.play_success()           # Major success
notifier.play_warning()           # Warning
notifier.play_error()             # Error
notifier.play_iteration()         # Subtle iteration sound

# Or use the enum
notifier.play(NotificationType.TASK_COMPLETE)
```

### Convenience Functions

```python
from sound_notifications import (
    play_task_complete,
    play_attention_needed,
    play_success,
    play_error,
    play_warning
)

# Simple function calls
play_task_complete()
play_attention_needed()
```

## Testing Sounds

### Test Individual Sounds

```bash
# Test a specific sound
python sound_notifications.py task_complete
python sound_notifications.py attention_needed
python sound_notifications.py success
python sound_notifications.py warning
python sound_notifications.py error
python sound_notifications.py iteration

# Test all sounds
python sound_notifications.py --test-all
```

### Interactive Demo

Run the interactive demo to see all sounds in context:

```bash
python demo_sounds.py
```

This will walk you through three scenarios:
1. Successful task completion
2. Max iterations reached
3. Error handling

## Sound Mappings

| Event | Sound | File | Description |
|-------|-------|------|-------------|
| Task Complete | Glass | Glass.aiff | Clean completion sound |
| Attention Needed | Ping | Ping.aiff | Alert sound requesting attention |
| Error | Basso | Basso.aiff | Low error tone |
| Success | Hero | Hero.aiff | Triumphant success fanfare |
| Warning | Funk | Funk.aiff | Quirky warning sound |
| Iteration | Tink | Tink.aiff | Subtle tick (non-intrusive) |

## When Sounds Play

### Ralph Loop Events

| Scenario | Sound | When |
|----------|-------|------|
| Verification incomplete | Tink | After each iteration that fails verification |
| Task verified complete | Hero | When verifier confirms task is complete |
| Max iterations reached | Funk | When iteration limit is hit |
| Max tokens reached | Funk | When token limit is hit |
| Max cost reached | Funk | When cost limit is hit |
| Exception/error | Basso | When an error occurs during execution |

## Configuration

### Global Settings

```python
from sound_notifications import get_notifier

notifier = get_notifier()

# Enable/disable globally
notifier.enable()
notifier.disable()

# Check status
is_enabled = notifier.enabled
```

### Custom Sound Directory

If you want to use custom sounds:

```python
from sound_notifications import SoundNotifier

notifier = SoundNotifier(
    enabled=True,
    sound_dir="/path/to/custom/sounds"
)
```

## Platform Support

Currently supports **macOS** using the built-in `afplay` command and system sounds from `/System/Library/Sounds/`.

Sounds play asynchronously by default (non-blocking), so they won't interrupt agent execution.

## Troubleshooting

### Sounds Not Playing

1. **Check volume**: Ensure system volume is not muted
2. **Check config**: Verify `enable_sounds=True` in config
3. **Check sound files**: Run `ls /System/Library/Sounds/` to verify sound files exist
4. **Test manually**: Run `afplay /System/Library/Sounds/Glass.aiff` to test audio

### Import Errors

If you see "Warning: Sound notifications not available", the module couldn't be imported. Ensure `sound_notifications.py` is in the same directory as `ralph_loop_agent.py`.

## Examples

### Minimal Example

```python
from ralph_loop_agent import RalphLoopAgent, RalphLoopConfig

# Sounds enabled by default
config = RalphLoopConfig(agent_type='docs', verbose=True)
ralph = RalphLoopAgent(config)
```

### With Custom Settings

```python
config = RalphLoopConfig(
    agent_type='coder',
    max_iterations=5,
    enable_sounds=True,
    verbose=True
)

ralph = RalphLoopAgent(config)
result = ralph.execute_loop(prompt, context, execute_fn)

# You'll hear:
# - Tink on each incomplete iteration
# - Hero when task completes successfully
# - Funk if max iterations is reached
# - Basso if an error occurs
```

### Selective Sounds

```python
from sound_notifications import get_notifier

notifier = get_notifier()

# Disable all sounds initially
notifier.disable()

# Enable only for important events
if task_is_critical:
    notifier.enable()
    
result = execute_task()

if result.success:
    notifier.play_success()
else:
    notifier.play_error()
```

## Best Practices

1. **Keep sounds enabled for long-running tasks** - Get notified when work completes
2. **Disable for batch processing** - Avoid sound spam when running many tasks
3. **Use verbose mode with sounds** - See what's happening while hearing progress
4. **Test sounds first** - Run `python sound_notifications.py --test-all` to familiarize yourself with each sound
5. **Consider context** - Disable sounds in shared workspaces or during meetings

## Future Enhancements

Potential future additions:
- Custom sound themes
- Volume control
- Cross-platform support (Linux, Windows)
- Notification center integration
- Sound profiles (loud, subtle, silent)
- Per-event sound customization
