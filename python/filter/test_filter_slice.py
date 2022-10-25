from filter_slice import filter_slice


tests = [
    [0, 1, 2],
    [0, None, 2],
    [None, 0, None, 2, None],
    [2, None, None, None, 0],
    [None, None, None, None],
]

for i, test in enumerate(tests):
    print(f'{i}:', filter_slice(test))
