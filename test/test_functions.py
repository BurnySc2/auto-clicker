import os
import sys
import pytest
from hypothesis import given
import hypothesis.strategies as st

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))


@pytest.mark.asyncio
async def test_something():
    pass


@pytest.mark.asyncio
@given(st.floats(allow_infinity=False, allow_nan=False))
async def test_do_math_floats(value):
    pass


@given(st.integers(min_value=0, max_value=10000))
def test_cpu_bound_summing(number):
    pass
