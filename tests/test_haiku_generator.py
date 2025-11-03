import textwrap

import pytest

from src.haiku_generator import DEFAULT_STRUCTURE, generate_haiku, iter_haiku


def test_generate_haiku_seeded_output():
    haiku = generate_haiku(seed=42)
    assert haiku == textwrap.dedent(
        """silent bamboo whispers
starlit wind linger softly
old forest stillness"""
    )


def test_iter_haiku_sequence_is_deterministic():
    haiku_list = list(iter_haiku(2, seed=5))
    assert haiku_list == [
        "silent mountain sunrise\ntwilight petals shimmer slowly\ntimeless pond stories",
        "quiet river whispers\ndawn cranes glimmer brightly\nold temple dreaming",
    ]


def test_iter_haiku_rejects_negative_counts():
    with pytest.raises(ValueError):
        list(iter_haiku(-1))


def test_custom_structure_works_with_generate():
    structure = type(DEFAULT_STRUCTURE)(lines=((("hello",), ("world",)),))
    haiku = generate_haiku(seed=1, structure=structure)
    assert haiku == "hello world"
