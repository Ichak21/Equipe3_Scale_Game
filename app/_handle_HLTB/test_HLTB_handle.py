from unittest.mock import MagicMock
import pandas as pd
import pytest

from HLTB_handle import HLTB_handle


def test_only_time_1_game():
    handle = HLTB_handle(True, False, False)
    resultat = handle.getDatas(["oblivion"])

    assert resultat.shape == (1, 7)


def test_only_count_1_game():
    handle = HLTB_handle(False, True, False)
    resultat = handle.getDatas(["oblivion"])

    assert resultat.shape == (1, 7)


def test_only_review_1_game():
    handle = HLTB_handle(False, False, True)
    resultat = handle.getDatas(["oblivion"])

    assert resultat.shape == (1, 5)


def test_full_4_games():
    handle = HLTB_handle(True, True, True)
    resultat = handle.getDatas(["oblivion", "fifa", "far cry", "call of duty"])

    assert resultat.shape == (4, 13)
