import sys
from diff import shortest_edit_script, DL, IN, EQ, Hunk

############ CONSTANTS ############

hunk_file = 'hunks.diff'
patched_file = 'result.c'

############           ############


def is_subsequence(a: list, b: list):
    '''
    Check if a is a subsequence of b.
    If a is a subsequence of b, return start index of a in b.
    Otherwise, return -1.
    '''
    if len(a) > len(b):
        return -1
    for i in range(len(b) - len(a) + 1):
        target = b[i:i + len(a)]

        if a == target:
            return i

    return None


def construct_splited_sequence(diffs: list, patched: bool):
    prefix = []
    middle = []
    postfix = []

    it = iter(diffs)
    d = next(it, None)

    while d is not None and d[0] == EQ:
        prefix += d[1]
        d = next(it, None)

    last_eq_pos = -1
    while d is not None:
        if not patched and d[0] == IN:
            d = next(it, None)
            continue
        if patched and d[0] == DL:
            d = next(it, None)
            continue
        middle += d[1]
        od = d[0]
        d = next(it, None)
        if d is not None and d[0] == EQ and od != EQ:
            last_eq_pos = len(middle)

    if last_eq_pos != -1:
        postfix = middle[last_eq_pos:]
        middle = middle[:last_eq_pos]

    return prefix, middle, postfix


def apply_hunk(old_sequence: list, hunk: Hunk, delta: int, offset_window=20):
    '''
    Apply a hunk to a sequence.
    If conflict is found, log and return old sequence, None.
    Return the new sequence, offset.
    '''
    npos = hunk.start2 + delta

    # Construct unmodified sequence from hunk
    unpre, unmid, unpos = construct_splited_sequence(hunk.diffs, False)
    unpatched_sequence = unpre + unmid + unpos
    is_sub = is_subsequence(
        unpatched_sequence, old_sequence[npos:npos + hunk.length1])

    # Check if modified sequence is a subsequence of old sequence
    if is_sub is None:
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
        if is_subsequence(patched_sequence, old_sequence[hunk.start2:hunk.start2 + hunk.length2]) is not None:
            # Modified sequence is a subsequence of old sequence,
            # Probably same patch is already applied ?
            return old_sequence, 0

    # Try finding in larger context and,
    windows_seq = old_sequence[max(0, npos-offset_window):
                               min(len(old_sequence), npos + hunk.length1 + offset_window)]

    if is_sub is None:
        # Try to find if there was something fully removed
        is_sub = is_subsequence(unmid, windows_seq)

        if is_sub is not None:
            is_sub -= (offset_window + len(unpre))

    if is_sub is None:
        # Try to find if there was something fully added
        is_sub = is_subsequence(unpre + unpos, windows_seq)

        if is_sub is not None:
            is_sub -= (offset_window + len(unpre))

    if is_sub is None:
        return old_sequence, None

    npos += is_sub

    for ed in hunk.diffs:
        op = ed[0]
        data = ed[1]
        if op == EQ:
            npos += len(data)
        elif op == IN:
            for ln in data:
                old_sequence.insert(npos, ln)
                npos += 1
        elif op == DL:
            for ln in data:
                old_sequence.pop(npos)

    return old_sequence, is_sub


def apply_patch(base_sequence: list, patched_sequence, target_sequence):

    hunks = shortest_edit_script(base_sequence, patched_sequence)

    # Log hunks to file
    with open(hunk_file, 'w') as f:
        f.truncate(0)
        for i, hunk in enumerate(hunks):
            print(f'%% Hunk #{i+1}', file=f)
            print(hunk, file=f)

    delta = 0
    for i, hunk in enumerate(hunks):
        target_sequence, offset = apply_hunk(target_sequence, hunk, delta)
        if offset is None:
            print(f'Hunk #{i+1} Failed', file=sys.stderr)
            delta += hunk.length1 - hunk.length2
        elif offset != 0:
            delta += offset
            print(f'Hunk #{i+1} Succeeded with offset {delta}', file=sys.stderr)

    return target_sequence


f1 = open(sys.argv[1]).read().splitlines()
f2 = open(sys.argv[2]).read().splitlines()
f3 = open(sys.argv[3]).read().splitlines()

f3_n = apply_patch(f1, f2, f3)

with open(patched_file, 'w') as f:
    f.truncate(0)
    f.write('\n'.join(f3_n))
