import sys
from diff import shortest_edit_script, DL, IN


def apply_patch(old_sequence: list, edit_script):
    delta = 0
    for i in range(len(edit_script)):
        hunk = edit_script[i]
        if hunk[0] == DL:
            for j in range(len(hunk[2])):
                seq = hunk[2][j]
                if seq == old_sequence[hunk[1] + delta]:
                    old_sequence.pop(hunk[1] + delta)
                    delta -= 1
                else:
                    print('Hunk Failed', i, j)
        elif hunk[0] == IN:
            for j in range(len(hunk[2])):
                old_sequence.insert(hunk[1] + delta, hunk[2][j])
                delta += 1

    return old_sequence


f1 = open(sys.argv[1]).read().splitlines()
f2 = open(sys.argv[2]).read().splitlines()
f3 = open(sys.argv[3]).read().splitlines()


# f1 = open(sys.argv[1]).read()
# f2 = open(sys.argv[2]).read()
# f3 = open(sys.argv[3]).read()


diffs = shortest_edit_script(f1, f2)

for diff in diffs:
    print(diff[0], diff[1] + 1, diff[2])

f3_n = apply_patch(f3, diffs)

print('\n'.join(f3_n))
# print(f1)
