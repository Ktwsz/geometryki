from set_state import find_intersections as set_find
from list_state import find_intersections as list_find
import numpy as np
import pandas as pd
from time import process_time


MAX_X = 200
MAX_Y = 200


def generate_uniform_sections(max_x, max_y, n):
    def generate_different(max_val, diff_set, n):
        tab = []

        while len(tab) < n:
            val = np.random.rand(1)[0] * max_val
            if val not in diff_set:
                tab.append(val)

        return tab

    def generate_without_rep(max_val, n):
        s = set()
        tab = []

        while len(s) < n:
            val = np.random.rand(1)[0] * max_val
            if val not in s:
                s.add(val)
                tab.append(val)

        return tab

    x1 = list(np.random.rand(n) * max_x)
    x2 = generate_without_rep(max_x, n)
    y1 = list(np.random.rand(n) * max_y)
    y2 = generate_different(max_y, y1, n)

    return [((x1[i], y1[i]), (x2[i], y2[i])) for i in range(n)]


comparison_df = pd.DataFrame(columns=["state_type", "size", "time"])


def n_range():
    n = 1e2
    for i in range(5):
        yield int(n)
        n += 1e2


def add_test(comparison_df, segments,  algorithm, df_dict):
    timer_start = process_time()
    _ = algorithm(segments)
    timer_stop = process_time()
    df_dict["time"] = round(timer_stop-timer_start, 3)
    comparison_df.loc[len(comparison_df)] = df_dict


def test():
    for n in n_range():
        segments = generate_uniform_sections(MAX_X, MAX_Y, n)

        add_test(comparison_df, segments, set_find, {"state_type": "set", "size": n})
        add_test(comparison_df, segments, list_find, {"state_type": "list", "size": n})

        print(n)

test()

comparison_df.to_csv('tests.csv', index=False)
