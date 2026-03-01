# Approve Pad

Universal approvals for terminals, editors, and AI prompts.

## What it does

Approve Pad provides an always-on-top control pad that sends fast approval inputs to the active window:

- `y{Enter}` (Yes / Allow)
- `n{Enter}` (No) — protected to reduce accidental rejects
- `1{Enter}`, `2{Enter}`, `3{Enter}` (option prompts)
- `a{Enter}` (Approve All / Always)

## Install

1. Install AutoHotkey v2
2. Run `src\Approve-Pad.ahk` (double-click)

## Quick use

- Click inside the prompt you want to answer (terminal or editor)
- Use the pad buttons
- Optional hotkeys:
  - Ctrl+Alt+L = Lock Target
  - Ctrl+Alt+P = Pause/Enable

## Notes

- If the target app runs as Admin, run Approve Pad as Admin too.
