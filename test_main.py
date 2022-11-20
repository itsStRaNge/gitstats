from main import *
from datetime import datetime
from pathlib import Path


def test_extraction():
    block = """
commit 001f407a04bb9802231f84713845e36b5358575f (origin/thesis_plotting)
Author: Lukas Bernhard <l.bernhard@tum.de>
Date:   Fri Apr 17 12:06:52 2020 +0200

    vae pipline runs, but weird behavoiur with loss

 src/__init__.py     | 4 ++--
 src/cvae/cnn.py     | 4 ++--
 src/utils/config.py | 2 +-
 3 files changed, 5 insertions(+), 5 deletions(-)
"""
    result = collect_stats_from_block(block)

    assert result == {
        "author": "l.bernhard@tum.de",
        "date": datetime(year=2020, month=4, day=17, hour=12, minute=6, second=52),
        "changes": [
            ("src/__init__.py", 4),
            ("src/cvae/cnn.py", 4),
            ("src/utils/config.py", 2),
        ]
    }


def test_extract_date():
    assert extract_date("Date:   Fri Apr 17 12:06:52 2020 +0200") == datetime(
        year=2020, month=4, day=17, hour=12, minute=6, second=52
    )
    assert extract_date("Date:   Fri Apr 1 12:06:52 2020 +0200") == datetime(
        year=2020, month=4, day=1, hour=12, minute=6, second=52
    )