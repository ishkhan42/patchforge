import sys
from diff import shortest_edit_script, DL, IN, EQ, Hunk


def apply_hunk(old_sequence: list, hunk: Hunk):
    '''
    Apply a hunk to a sequence.
    If conflict is found, log and return old sequence.
    Return the new sequence.
    '''
    st1 = hunk.start1
    st2 = hunk.start2

    for ed in hunk.diffs:
        op = ed[0]
        data = ed[1]
        if op == EQ:
            st1 += len(data)
            st2 += len(data)
        if op == IN:
            for ln in data:
                old_sequence.insert(st2, ln)
                st1 += 1
                st2 += 1
        if op == DL:
            for ln in data:
                old_sequence.pop(st2)
    return old_sequence


def apply_patch(old_sequence: list, hunks: list[Hunk]):
    for hunk in hunks:
        old_sequence = apply_hunk(old_sequence, hunk)

    return old_sequence


f1 = open(sys.argv[1]).read().splitlines()
f2 = open(sys.argv[2]).read().splitlines()
f3 = open(sys.argv[3]).read().splitlines()


# f1 = open(sys.argv[1]).read()
# f2 = open(sys.argv[2]).read()
# f3 = open(sys.argv[3]).read()


hunks = shortest_edit_script(f1, f2)

# for diff in diffs:
#     print(diff[0], diff[1] + 1, diff[2])

f3_n = apply_patch(f3, hunks)

print('\n'.join(f3_n))
# print(f1)
