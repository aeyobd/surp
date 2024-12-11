import pytest
import surp
import pandas as pd


def test_vincenzo():
    v21 = surp.vincenzo2021()
    assert isinstance(v21, pd.DataFrame)
