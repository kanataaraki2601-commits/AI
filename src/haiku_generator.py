"""Simple haiku generator with a tiny curated vocabulary.

This module provides a deterministic haiku generator that can be used as a
command-line script or imported as a library. Each haiku follows the
traditional 5-7-5 syllable structure using preset vocabulary that roughly
matches syllable counts. The vocabulary is intentionally small to keep the
implementation approachable while still allowing playful combinations.
"""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Iterable, List, Sequence


@dataclass(frozen=True)
class HaikuStructure:
    """Represents the structure of a haiku using lists of word options.

    Each element of ``lines`` corresponds to a line in the haiku. The list for
    a line contains tuples of candidate fragments; when a haiku is generated,
    one fragment from each tuple is chosen.
    """

    lines: Sequence[Sequence[Sequence[str]]]

    def compose(self, rng: Random) -> List[str]:
        """Compose a haiku using the provided random number generator."""

        composed_lines: List[str] = []
        for line_options in self.lines:
            fragments = [rng.choice(options) for options in line_options]
            composed_lines.append(" ".join(fragments))
        return composed_lines


DEFAULT_STRUCTURE = HaikuStructure(
    lines=(
        (
            ("quiet", "gentle", "silent"),
            ("bamboo", "mountain", "river"),
            ("whispers", "echoes", "sunrise"),
        ),
        (
            ("dawn", "twilight", "starlit"),
            ("cranes", "wind", "petals"),
            ("linger", "glimmer", "shimmer"),
            ("softly", "brightly", "slowly"),
        ),
        (
            ("old", "ancient", "timeless"),
            ("pond", "temple", "forest"),
            ("stillness", "stories", "dreaming"),
        ),
    )
)


def generate_haiku(seed: int | None = None, structure: HaikuStructure = DEFAULT_STRUCTURE) -> str:
    """Generate a three-line haiku.

    Args:
        seed: Optional seed to make the output deterministic.
        structure: The structure that defines fragment choices for each line.

    Returns:
        A string containing a three-line haiku.
    """

    rng = Random(seed)
    lines = structure.compose(rng)
    return "\n".join(lines)


def iter_haiku(count: int, seed: int | None = None, *, structure: HaikuStructure = DEFAULT_STRUCTURE) -> Iterable[str]:
    """Yield ``count`` haiku strings.

    The generator advances the internal state of ``rng`` so each haiku is
    unique (unless the structure or vocabulary is tiny enough to cause
    collisions).
    """

    if count < 0:
        raise ValueError("count must be non-negative")

    rng = Random(seed)
    for _ in range(count):
        yield "\n".join(structure.compose(rng))


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for ``python -m src.haiku_generator``.

    Supported arguments:
        * ``--count``: Number of haiku to emit (defaults to 1).
        * ``--seed``: Integer seed for deterministic output.
    """

    import argparse

    parser = argparse.ArgumentParser(description="Generate playful haiku.")
    parser.add_argument("--count", type=int, default=1, help="Number of haiku to output")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed for deterministic output")
    args = parser.parse_args(argv)

    for haiku in iter_haiku(args.count, seed=args.seed):
        print(haiku)
        print()
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
