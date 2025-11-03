#!/usr/bin/env python3
"""Terminal-based adventure game: Maze Runner.

The player explores a grid, gathers artifacts, avoids traps, and escapes
before being caught by a roaming guardian.
"""

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional, Tuple


Position = Tuple[int, int]


BOARD_SIZE = 7
NUM_TREASURES = 4
NUM_TRAPS = 5
PLAYER_HEALTH = 5
MAX_HEALTH = 7


@dataclass
class Relic:
    name: str
    description: str
    effect: str


@dataclass
class Player:
    position: Position
    health: int = PLAYER_HEALTH
    score: int = 0
    inventory: List["Relic"] = None
    shield_charges: int = 0
    blink_available: bool = False
    sense_direction: bool = False
    exit_hint: bool = False
    pulse_available: bool = True

    def __post_init__(self) -> None:
        if self.inventory is None:
            self.inventory = []

    def move(self, direction: str) -> None:
        dx, dy = DIRECTIONS[direction]
        x, y = self.position
        self.position = (x + dx, y + dy)


@dataclass
class Guardian:
    position: Position

    def chase(self, target: Position, occupied: Iterable[Position]) -> None:
        # Guardian attempts to move closer to the player while avoiding
        # stepping onto tiles that are already occupied.
        x, y = self.position
        tx, ty = target
        candidates: List[Position] = []

        if tx > x:
            candidates.append((x + 1, y))
        elif tx < x:
            candidates.append((x - 1, y))

        if ty > y:
            candidates.append((x, y + 1))
        elif ty < y:
            candidates.append((x, y - 1))

        # If aligned with the player, consider orthogonal moves for variety.
        if not candidates:
            candidates.extend(
                [
                    (x + 1, y),
                    (x - 1, y),
                    (x, y + 1),
                    (x, y - 1),
                ]
            )

        random.shuffle(candidates)
        for nx, ny in candidates:
            if within_bounds((nx, ny)) and (nx, ny) not in occupied:
                self.position = (nx, ny)
                return

        # If no move was valid, stay in place.


DIRECTIONS: Dict[str, Position] = {
    "w": (-1, 0),
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
}


def within_bounds(position: Position) -> bool:
    x, y = position
    return 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE


def random_positions(count: int, exclude: Optional[Iterable[Position]] = None) -> List[Position]:
    exclude_set = set(exclude or [])
    positions = []
    while len(positions) < count:
        pos = (random.randrange(BOARD_SIZE), random.randrange(BOARD_SIZE))
        if pos in exclude_set:
            continue
        if pos in positions:
            continue
        positions.append(pos)
    return positions


def manhattan_distance(a: Position, b: Position) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def nearest_position(origin: Position, targets: Iterable[Position]) -> Optional[Position]:
    targets_list = list(targets)
    if not targets_list:
        return None
    return min(targets_list, key=lambda pos: manhattan_distance(origin, pos))


RELIC_LIBRARY: List[Relic] = [
    Relic(
        name="Sunfire Sigil",
        description="It radiates warmth that closes your wounds.",
        effect="heal",
    ),
    Relic(
        name="Thornweave Mantle",
        description="Vines coil around you, eager to shield you from harm.",
        effect="shield",
    ),
    Relic(
        name="Blinkstone",
        description="The gem hums, promising an escape from certain doom.",
        effect="blink",
    ),
    Relic(
        name="Echo Compass",
        description="Its needle thrums toward danger, revealing the guardian's stride.",
        effect="sense",
    ),
    Relic(
        name="Star Map Fragment",
        description="Constellations rearrange to highlight a hidden exit path.",
        effect="exit_hint",
    ),
    Relic(
        name="Chrono Beetle",
        description="A mechanical beetle that nibbles at time, boosting your insight.",
        effect="score",
    ),
]


def generate_relic() -> Relic:
    return random.choice(RELIC_LIBRARY)


def describe_tile(tile: str) -> str:
    descriptions = {
        "T": "a glittering relic",
        "X": "an ancient snare",
        "G": "the stone guardian",
        "E": "the shimmering exit",
    }
    return descriptions.get(tile, "something unsettling")


def build_board(
    player: Player,
    guardian: Guardian,
    treasures: List[Position],
    traps: List[Position],
    exit_tile: Position,
) -> List[List[str]]:
    board = [["." for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
    for tx, ty in treasures:
        board[tx][ty] = "T"
    for tx, ty in traps:
        board[tx][ty] = "X"
    gx, gy = guardian.position
    board[gx][gy] = "G"
    ex, ey = exit_tile
    board[ex][ey] = "E"
    px, py = player.position
    board[px][py] = "P"
    return board


def display_board(board: List[List[str]], reveal: bool = False) -> None:
    legend = {"P": "🧭", "G": "🗿", "T": "💎", "X": "⚠", "E": "🚪", ".": "·"}
    for row in board:
        display_row = []
        for cell in row:
            if cell in {"T", "X", "G", "E"} and not reveal:
                display_row.append("·")
            else:
                display_row.append(legend.get(cell, cell))
        print(" ".join(display_row))


def initial_state() -> Tuple[Player, Guardian, List[Position], List[Position], Position]:
    center = BOARD_SIZE // 2
    player = Player(position=(center, center))
    # Reserve the center for the player, then sample other tiles.
    positions = random_positions(1 + NUM_TREASURES + NUM_TRAPS + 1, exclude=[player.position])
    guardian_pos = positions[0]
    treasure_positions = positions[1 : 1 + NUM_TREASURES]
    trap_positions = positions[1 + NUM_TREASURES : 1 + NUM_TREASURES + NUM_TRAPS]
    exit_position = positions[-1]
    guardian = Guardian(position=guardian_pos)
    return player, guardian, treasure_positions, trap_positions, exit_position


def is_blocked(position: Position, traps: Iterable[Position]) -> bool:
    return position in traps or not within_bounds(position)


def attempt_move(player: Player, direction: str, traps: Iterable[Position]) -> bool:
    dx, dy = DIRECTIONS[direction]
    x, y = player.position
    new_pos = (x + dx, y + dy)
    if not within_bounds(new_pos):
        print("You bump into a wall of twisting roots. Try another way.")
        return False
    player.position = new_pos
    return True


def resolve_tile(player: Player, tile: str) -> None:
    if tile == "T":
        relic = generate_relic()
        player.inventory.append(relic)
        player.score += 15
        print(f"You pocket the {relic.name}! {relic.description}")
        apply_relic_effect(player, relic)
    elif tile == "X":
        if player.shield_charges > 0:
            player.shield_charges -= 1
            print("Your thornweave mantle absorbs the trap's impact!")
        else:
            player.health -= 1
            print("Spikes lash out! You grit your teeth and push forward (-1 health).")
    elif tile == "E":
        print("The exit hums with energy. If you have relics, freedom awaits!")
    elif tile == "G":
        player.health -= 2
        print("The guardian crushes you with a stone fist (-2 health). Run!")


def guardian_turn(
    guardian: Guardian,
    player: Player,
    traps: Iterable[Position],
    treasures: Iterable[Position],
    exit_tile: Position,
) -> None:
    steps = 1 + len(player.inventory) // 2
    if steps > 1:
        print("The guardian surges with fury, accelerating its pursuit!")

    for _ in range(steps):
        guardian.chase(player.position, occupied=set(traps))
        if guardian.position == player.position:
            if player.blink_available:
                blink_escape(player, guardian, traps, treasures, exit_tile)
                break
            player.health -= 2
            print("The guardian catches up and slams you again (-2 health)!")
            break


def blink_escape(
    player: Player,
    guardian: Guardian,
    traps: Iterable[Position],
    treasures: Iterable[Position],
    exit_tile: Position,
) -> None:
    player.blink_available = False
    occupied = set(traps)
    occupied.update(treasures)
    occupied.add(guardian.position)
    occupied.add(exit_tile)

    safe_tiles = [
        (x, y)
        for x in range(BOARD_SIZE)
        for y in range(BOARD_SIZE)
        if (x, y) not in occupied and (x, y) != player.position
    ]
    if not safe_tiles:
        print("The Blinkstone flickers but finds no refuge! You brace for impact.")
        player.health -= 2
        print("The guardian catches up and slams you again (-2 health)!")
        return

    new_position = random.choice(safe_tiles)
    player.position = new_position
    print("The Blinkstone flares, wrenching you through space to safety!")


def tile_at(position: Position, treasures: List[Position], traps: List[Position], exit_tile: Position, guardian: Guardian) -> str:
    if position == guardian.position:
        return "G"
    if position == exit_tile:
        return "E"
    if position in treasures:
        return "T"
    if position in traps:
        return "X"
    return "."


def remove_tile(position: Position, treasures: List[Position], traps: List[Position]) -> None:
    if position in treasures:
        treasures.remove(position)
    if position in traps:
        traps.remove(position)


def apply_relic_effect(player: Player, relic: Relic) -> None:
    if relic.effect == "heal":
        if player.health < MAX_HEALTH:
            player.health = min(MAX_HEALTH, player.health + 1)
            print("The warmth mends your wounds (+1 health).")
        else:
            player.score += 5
            print("You already feel invigorated, so the sigil boosts your confidence (+5 score).")
    elif relic.effect == "shield":
        player.shield_charges += 1
        print("Thorny vines encase you, ready to absorb the next trap strike.")
    elif relic.effect == "blink":
        player.blink_available = True
        print("You feel space bend around you. The Blinkstone will trigger if the guardian corners you.")
    elif relic.effect == "sense":
        if not player.sense_direction:
            player.sense_direction = True
            print("You now sense the guardian's precise approach each turn.")
        else:
            player.score += 5
            print("The compass resonates with your instincts (+5 score).")
    elif relic.effect == "exit_hint":
        player.exit_hint = True
        print("Star lines point toward the exit. You can now feel its direction.")
    elif relic.effect == "score":
        player.score += 10
        print("Time slows for a heartbeat (+10 score).")


def status(player: Player, guardian: Guardian, treasures: List[Position], exit_tile: Position) -> None:
    print(
        f"Health: {player.health}   Relics: {len(player.inventory)}   Score: {player.score}   Shield charges: {player.shield_charges}"
    )
    distance = abs(player.position[0] - guardian.position[0]) + abs(player.position[1] - guardian.position[1])
    if player.sense_direction:
        direction_hint = guardian_direction_hint(player.position, guardian.position)
        hint = f"You feel the guardian {direction_hint} (distance {distance})."
    else:
        hint = "The guardian's footsteps echo nearby!" if distance <= 2 else "All seems quiet... for now."
    print(hint)
    if player.exit_hint:
        print(f"A tug in your gut says the exit lies {exit_direction_hint(player.position, exit_tile)}")
    print(f"Relics remaining: {len(treasures)}")
    if player.pulse_available:
        print("Mystic pulse ready (press 'p').")


def guardian_direction_hint(player_pos: Position, guardian_pos: Position) -> str:
    return compose_direction_hint(player_pos, guardian_pos, subject="approaches", preposition="from")


def exit_direction_hint(player_pos: Position, exit_tile: Position) -> str:
    return compose_direction_hint(player_pos, exit_tile, subject="pulls", preposition="toward")


def compose_direction_hint(origin: Position, target: Position, subject: str, preposition: str) -> str:
    ox, oy = origin
    tx, ty = target
    directions: List[str] = []
    if tx < ox:
        directions.append("north")
    elif tx > ox:
        directions.append("south")
    if ty < oy:
        directions.append("west")
    elif ty > oy:
        directions.append("east")

    if not directions:
        return f"{subject} right beside you"
    if len(directions) == 2:
        direction_phrase = f"{directions[0]} and {directions[1]}"
    else:
        direction_phrase = directions[0]
    return f"{subject} {preposition} the {direction_phrase}"


def mystic_pulse(
    player: Player,
    treasures: Iterable[Position],
    exit_tile: Position,
    guardian: Guardian,
) -> None:
    player.pulse_available = False
    print("You unleash a mystic pulse. For a heartbeat, the maze reveals itself!")
    nearest_relic = nearest_position(player.position, treasures)
    if nearest_relic:
        print(
            f"A relic glimmers {compose_direction_hint(player.position, nearest_relic, subject='waiting', preposition='to')}"
            f" {manhattan_distance(player.position, nearest_relic)} steps away."
        )
    else:
        print("No more relics answer your call.")

    print(
        f"The exit {compose_direction_hint(player.position, exit_tile, subject='pulls', preposition='toward')}"
        f" at a distance of {manhattan_distance(player.position, exit_tile)}."
    )
    print(
        f"You sense the guardian {compose_direction_hint(player.position, guardian.position, subject='lurking', preposition='from')}"
        f" at {manhattan_distance(player.position, guardian.position)} steps."
    )


def trigger_ambient_event(
    player: Player,
    guardian: Guardian,
    exit_tile: Position,
    treasures: Iterable[Position],
    traps: Iterable[Position],
) -> None:
    if random.random() >= 0.3:
        return

    events = []
    if player.health < MAX_HEALTH:
        events.append("healing")
    if list(traps):
        events.append("trap_hint")
    events.extend(["memory", "rumble"])

    event = random.choice(events)
    if event == "healing":
        player.health = min(MAX_HEALTH, player.health + 1)
        print("Luminescent spores settle on you, knitting your wounds (+1 health).")
    elif event == "trap_hint":
        nearest_trap = nearest_position(player.position, traps)
        if nearest_trap:
            direction = compose_direction_hint(player.position, nearest_trap, subject="warns", preposition="of")
            print(
                f"A whisper in the vines {direction}; a snare lurks {manhattan_distance(player.position, nearest_trap)} steps away."
            )
    elif event == "memory":
        player.score += 5
        print("A lost explorer's memory floods your mind (+5 score).")
    elif event == "rumble":
        distance = manhattan_distance(player.position, guardian.position)
        print(f"The maze trembles as the guardian roars somewhere {distance} steps away.")


def intro() -> None:
    print(
        """
Welcome to MAZE RUNNER
----------------------
You awaken in a living labyrinth. Relics within the maze will power the exit,
but a relentless stone guardian roams the halls. Gather relics, avoid traps,
and find the portal before the guardian crushes you.

Controls: w (up), a (left), s (down), d (right), q (quit)
Tip: Listen to the guardian's footsteps and trust your instincts!
"""
    )


def check_victory(player: Player, exit_tile: Position) -> bool:
    if player.position != exit_tile:
        return False
    if player.inventory:
        print("The relics resonate with the portal. You surge into the light! You win!")
        player.score += 25
        return True
    print("The portal rejects you. It needs the relics' energy!")
    return False


def play(
    command_provider: Optional[
        Callable[[Player, Guardian, List[Position], List[Position], Position], str]
    ] = None,
    *,
    seed: Optional[int] = None,
    max_turns: Optional[int] = None,
) -> None:
    if seed is not None:
        random.seed(seed)

    intro()
    player, guardian, treasures, traps, exit_tile = initial_state()
    turns_taken = 0

    while player.health > 0:
        board = build_board(player, guardian, treasures, traps, exit_tile)
        display_board(board)
        status(player, guardian, treasures, exit_tile)

        if command_provider is not None:
            command = command_provider(player, guardian, treasures, traps, exit_tile)
            print(f"Demo move: {command}")
        else:
            command = input("Your move: ").strip().lower()
        if command == "q":
            print("You sit down and accept your fate. Game over.")
            return
        if command == "p":
            if player.pulse_available:
                mystic_pulse(player, treasures, exit_tile, guardian)
            else:
                print("Your mystic pulse is spent. The maze remains silent.")
            if command_provider is not None:
                turns_taken += 1
            guardian_turn(guardian, player, traps, treasures, exit_tile)
            if player.health <= 0:
                break
            if (
                command_provider is not None
                and max_turns is not None
                and turns_taken >= max_turns
            ):
                print("\nDemo turn limit reached. Ending the run.")
                break
            continue
        if command not in DIRECTIONS:
            print("Unrecognized action. Use w, a, s, d, or q.")
            continue

        if not attempt_move(player, command, traps):
            continue

        tile = tile_at(player.position, treasures, traps, exit_tile, guardian)
        if tile != ".":
            print(f"You encounter {describe_tile(tile)}!")
            resolve_tile(player, tile)
            remove_tile(player.position, treasures, traps)
            if player.health <= 0:
                break
        else:
            trigger_ambient_event(player, guardian, exit_tile, treasures, traps)

        if check_victory(player, exit_tile):
            break

        guardian_turn(guardian, player, traps, treasures, exit_tile)
        if player.health <= 0:
            break

        turns_taken += 1
        if command_provider is not None and max_turns is not None:
            if turns_taken >= max_turns:
                print("\nDemo turn limit reached. Ending the run.")
                break

    print("\nThe labyrinth claims another adventurer...")
    print(f"Final score: {player.score}")
    print("Revealing the final layout:")
    final_board = build_board(player, guardian, treasures, traps, exit_tile)
    display_board(final_board, reveal=True)


def demo_command_provider_factory() -> Callable[
    [Player, Guardian, List[Position], List[Position], Position],
    str,
]:
    """Create a simple AI that showcases the game without user input."""

    pulse_used = False

    def provider(
        player: Player,
        guardian: Guardian,
        treasures: List[Position],
        traps: List[Position],
        exit_tile: Position,
    ) -> str:
        nonlocal pulse_used

        if player.pulse_available and not pulse_used:
            pulse_used = True
            return "p"

        targets = treasures or [exit_tile]
        target = min(targets, key=lambda pos: manhattan_distance(player.position, pos))

        px, py = player.position
        tx, ty = target
        candidate_moves: List[str] = []

        if tx < px:
            candidate_moves.append("w")
        if tx > px:
            candidate_moves.append("s")
        if ty < py:
            candidate_moves.append("a")
        if ty > py:
            candidate_moves.append("d")

        random.shuffle(candidate_moves)
        candidate_moves.extend([move for move in DIRECTIONS if move not in candidate_moves])

        for move in candidate_moves:
            nx, ny = px + DIRECTIONS[move][0], py + DIRECTIONS[move][1]
            if within_bounds((nx, ny)):
                return move

        return "q"

    return provider


def run_demo(seed: Optional[int], max_turns: int) -> None:
    """Run an automated demo session for quick previews."""

    if seed is None:
        random.seed()
    provider = demo_command_provider_factory()
    play(command_provider=provider, seed=seed, max_turns=max_turns)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Maze Runner terminal adventure")
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run an automated demo instead of the interactive game.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed the random number generator for reproducible runs.",
    )
    parser.add_argument(
        "--turns",
        type=int,
        default=60,
        help="Maximum number of turns the demo should play before exiting.",
    )
    args = parser.parse_args()

    if args.demo:
        run_demo(args.seed, args.turns)
    else:
        if args.seed is not None:
            random.seed(args.seed)
        else:
            random.seed()
        play()
