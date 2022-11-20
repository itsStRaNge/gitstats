import re
import subprocess
from pathlib import Path
from subprocess import PIPE
import os
from datetime import datetime
import pandas as pd
import plotly.express as px

TARGET_REPO = r"D:\GitProjects\numpy"
START_DATE = "2022-01-01"


def main():
    os.chdir(TARGET_REPO)
    result = subprocess.run(
        ['git', 'log', '--stat', f'--after={START_DATE}'],
        stdout=PIPE, stderr=PIPE, universal_newlines=True, encoding="utf8"
    )

    stats = []
    for block in result.stdout.split('commit'):
        try:
            stats += collect_stats_from_block(block)
        except Exception:
            pass
    df = pd.DataFrame(stats)
    df['lines'] = df['file'].apply(extract_file_length)
    # todo: check against all currently existing files, so that all current files are displayed and untouched files have 0 change
    # todo: create metric to show knowledge silos of developers and how much they know about the code base
    
    plot_hotspots(df)


def collect_stats_from_block(block: str) -> [{}]:
    date = extract_date(block)
    author = re.search('<(.*)>', block).group(1)
    changes = extract_changes(block)
    return [{
        'author': author,
        'date': date,
        'file': ch[0],
        'changes': ch[1]
    } for ch in changes]


def extract_date(block: str) -> datetime:
    date = re.search(r'\S{3} \d{2} \d{2}:\d{2}:\d{2} \d{4}', block)
    if not date:
        date = re.search(r'\S{3} \d \d{2}:\d{2}:\d{2} \d{4}', block)
    return datetime.strptime(date.group(), "%b %d %H:%M:%S %Y")


def extract_changes(block: str) -> (str, int):
    matches = re.findall(r"\S+\s+\|\s\d", block)
    changes = []
    for m in matches:
        m = m.split(" | ")
        changes.append((m[0].strip(), int(m[1].strip())))
    return changes


def extract_file_length(x) -> int:
    try:
        with open(x, 'r', encoding="utf8") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def plot_hotspots(df: pd.DataFrame):
    df = df.groupby('file').sum(numeric_only=True)
    df['changes'] = ((df-df.min())/(df.max()-df.min()))['changes']
    hierarchies = explode_folder_structure(df)
    df = df.merge(hierarchies, left_index=True, right_index=True)
    df = df[df['lines'] != 0]
    df = df.replace(r'^\s*$', "root", regex=True)
    fig = px.treemap(
        df, path=hierarchies.columns, values='lines', color='changes',
        color_continuous_scale='matter', color_continuous_midpoint=.5
    )
    fig.show()


def explode_folder_structure(df: pd.DataFrame) -> (pd.DataFrame, int):
    df = pd.DataFrame(df.index.to_series().apply(
        lambda x: Path(x).parts
    ).to_list(), index=df.index)
    return df


if __name__ == '__main__':
    main()