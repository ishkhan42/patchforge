import sys
from diff import shortest_edit_script, DL, IN, EQ, Hunk


def is_subsequence(a: list, b: list):
    '''
    Check if a is a subsequence of b.
    If a is a subsequence of b, return start index of a in b.
    Otherwise, return -1.
    '''
    if len(a) > len(b):
        return -1
    # print('Checking subsequence:', file=sys.stderr)
    for i in range(len(b) - len(a) + 1):
        # print(b[i:i + len(a)] == a, '\n', b[i:i + len(a)], '\n', a, file=sys.stderr)
        target = b[i:i + len(a)]
        if target == a:
            return i
        # yes = True
        # for j in range(len(a)):
        #     if a[j] != target[j]:
        #         yes = False
        #         print('Not a subsequence:', a[j], file=sys.stderr)
        #         break

        # if yes:
        #     return i
    return -1


def apply_hunk(old_sequence: list, hunk: Hunk, delta: int):
    '''
    Apply a hunk to a sequence.
    If conflict is found, log and return old sequence.
    Return the new sequence.
    '''
    st1 = hunk.start1 + delta
    st2 = hunk.start2 + delta

    # Construct unmodified sequence from hunk
    unpatched_sequence = []
    for ed in hunk.diffs:
        op = ed[0]
        data = ed[1]
        if op == EQ:
            unpatched_sequence += data
        if op == DL:
            unpatched_sequence += data
        if op == IN:
            pass

    # Debug print upatched sequence
    # print('Unpatched sequence:', file=sys.stderr)
    # for ln in unpatched_sequence:
    #     print(ln, file=sys.stderr)

    is_sub = is_subsequence(
        unpatched_sequence, old_sequence[st2:st2 + hunk.length1])
    # print('is_sub:', is_sub, file=sys.stderr)

    if is_sub == -1:
        # Construct modified sequence from hunk
        patched_sequence = []
        for ed in hunk.diffs:
            op = ed[0]
            data = ed[1]
            if op == EQ:
                patched_sequence += data
            if op == DL:
                pass
            if op == IN:
                patched_sequence += data
        if is_subsequence(patched_sequence, old_sequence[hunk.start2:hunk.start2 + hunk.length2]) != -1:
            # Modified sequence is a subsequence of old sequence,
            # Probably same patch applied is already applied ?
            return old_sequence, True

    if is_sub == -1:
        # No subsequence found, probably conflict
        print('Conflict found at line', st2 + 1, file=sys.stderr)
        return old_sequence, False

    st1 += is_sub
    st2 += is_sub

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

    return old_sequence, True


def apply_patch(old_sequence: list, hunks: list[Hunk]):
    delta = 0
    for hunk in hunks:
        old_sequence, res = apply_hunk(old_sequence, hunk, delta)
        if not res:
            delta += hunk.length2

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
