# Maze Runner

This repository contains a terminal adventure game where you explore a living
labyrinth, gather relics, and race against a roaming stone guardian.

## How to Play

```bash
python game.py
```

Use `w`, `a`, `s`, and `d` to move, `p` to unleash a one-time mystic pulse that
reveals nearby secrets, and `q` to quit. Collect relics before reaching the
exit to escape successfully. Beware of traps and the guardian!

### What Makes This Run Interesting

* **Living relics** – every relic you grab grants an immediate boon such as
  healing light, trap-negating thorn armor, a one-time Blinkstone escape, or
  heightened senses that track the guardian and exit.
* **Escalating guardian** – the stone guardian grows faster as you hoard relics
  and can take multiple steps per turn. If it corners you, the Blinkstone (if
  found) automatically warps you to a random safe tile.
* **Ambient events** – empty tiles might still hide glowing spores, whispered
  warnings about nearby traps, or echoes of past explorers that boost your
  score.
* **Mystic pulse** – once per game you can pause to pulse the maze, revealing
  distances and directions to the nearest relic, the exit, and the guardian.
