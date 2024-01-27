import math
import sys
import urllib.parse

'''
Referances:
http://www.xmailserver.org/diff2.pdf (An O(ND) Difference Algorithm and Its Variations' by EUGENE W. MYERS.)
https://blog.robertelder.org/diff-algorithm/
'''

DL = -1
IN = 1
EQ = 0


class Hunk:

    def __init__(self):
        self.diffs: list = []
        self.start1 = None
        self.start2 = None
        self.length1 = 0
        self.length2 = 0

    def __str__(self):
        """
        Similar to GNU diff's output.
        """
        if self.length1 == 0:
            coords1 = str(self.start1) + ",0"
        elif self.length1 == 1:
            coords1 = str(self.start1 + 1)
        else:
            coords1 = str(self.start1 + 1) + "," + str(self.length1)
        if self.length2 == 0:
            coords2 = str(self.start2) + ",0"
        elif self.length2 == 1:
            coords2 = str(self.start2 + 1)
        else:
            coords2 = str(self.start2 + 1) + "," + str(self.length2)
        text = ["@@ -", coords1, " +", coords2, " @@\n"]

        # Escape the body of the patch with %xx notation.
        for (op, data) in self.diffs:
            o = ' '
            if op == IN:
                o = '+'
            elif op == DL:
                o = '-'

            if isinstance(data, list):
                form = ""
                for l in data:
                    form += o + l + "\n"
            else:
                form = o + data

            # High ascii will raise UnicodeDecodeError.  Use Unicode instead.
            # data = data.encode("utf-8")
            # text.append(urllib.parse.quote(data, "!~*'();/?:@&=+$,# ") + "\n")
            text.append(form)
        return "".join(text)


def find_middle_snake(old_sequence, new_sequence):
    """
    Returns 5 integers:
    - number of edits
    - starting x coordinate of the snake
    - starting y coordinate of the snake
    - ending x coordinate of the snake
    - ending y coordinate of the snake
    """
    old_len = len(old_sequence)
    new_len = len(new_sequence)
    max_len = old_len + new_len
    delta = old_len - new_len

    arr_len = 2 * min(new_len, old_len) + 2
    arr_fwd = [None] * arr_len  # Forward direction
    arr_bwd = [None] * arr_len  # Backward direction
    arr_fwd[1] = 0
    arr_bwd[1] = 0
    x = None

    max_diags = math.ceil(max_len / 2)  # Maximum number of diagonals
    for nde in range(0, max_diags + 1):  # nde - count of non diagonal edges in the path

        start_diag = -(nde - 2 * max(0, nde - new_len))  # index of first diagonal
        end_diag = nde - 2 * max(0, nde - old_len)  # index of last diagonal

        #### Forward direction ####
        #### Mutated global variables ####
        #### arr_fwd ####
        for did in range(start_diag, end_diag + 1, 2):  # did - diagonal index

            if did == -nde or \
                    did != nde and arr_fwd[(did - 1) % arr_len] < arr_fwd[(did + 1) % arr_len]:
                x = arr_fwd[(did + 1) % arr_len]
            else:
                x = arr_fwd[(did - 1) % arr_len] + 1

            y = x - did

            # Starting x and y coordinates for the current snake
            x_i = x
            y_i = y
            while x < old_len and y < new_len and old_sequence[x] == new_sequence[y]:
                x += 1
                y += 1
            arr_fwd[did % arr_len] = x

            inverse_k = (-(did - delta))
            if (delta % 2 == 1) and inverse_k >= -(nde - 1) and inverse_k <= (nde - 1):
                if arr_fwd[did % arr_len] + arr_bwd[inverse_k % arr_len] >= old_len:
                    return 2 * nde - 1, x_i, y_i, x, y

        #### Backward direction ####
        #### Mutated global variables ####
        #### arr_bwd ####
        for did in range(start_diag, end_diag + 1, 2):
            if did == -nde or did != nde and arr_bwd[(did - 1) % arr_len] < arr_bwd[(did + 1) % arr_len]:
                x = arr_bwd[(did + 1) % arr_len]
            else:
                x = arr_bwd[(did - 1) % arr_len] + 1
            y = x - did
            x_i = x
            y_i = y
            while x < old_len and y < new_len and old_sequence[old_len - x - 1] == new_sequence[new_len - y - 1]:
                x += 1
                y += 1
            arr_bwd[did % arr_len] = x
            inverse_k = (-(did - delta))
            if (delta % 2 == 0) and inverse_k >= -nde and inverse_k <= nde:
                if arr_bwd[did % arr_len] + arr_fwd[inverse_k % arr_len] >= old_len:
                    return 2 * nde, old_len - x, new_len - y, old_len - x_i, new_len - y_i


def shortest_edit_script(old_sequence, new_sequence, ctx_len=3):
    old_len = len(old_sequence)
    new_len = len(new_sequence)
    trace = []

    stack = [(0, 0, old_len, new_len)]
    while len(stack) > 0:
        current_x, current_y, old_len, new_len = stack.pop()
        if old_len > 0 and new_len > 0:
            # x and y are starting coordinates of the snake
            # u and v are ending coordinates of the snake
            edits, x, y, u, v = find_middle_snake(
                old_sequence[current_x:current_x + old_len], new_sequence[current_y:current_y + new_len])

            # If not a base case with one edit, or if we have a snake, then divide
            if edits > 1 or (x != u and y != v):
                # Before snake
                stack.append((current_x + u, current_y + v, old_len - u, new_len - v))
                # After snake
                stack.append((current_x, current_y, x, y))
            elif new_len > old_len:
                # TL;DR: Found a single insertion.
                #  new_len is longer than old_len, but we know there is a maximum of one edit to transform old_sequence into new_sequence
                #  The first old_len elements of both sequences in this case will represent the snake, and the last element
                #  will represent a single insertion.
                stack.append((current_x + old_len, current_y + old_len, 0, new_len - old_len))
            elif new_len < old_len:
                # TL;DR: Found a single deletion.
                #  old_len is longer than new_len, but we know there is a maximum of one edit to transform old_sequence into new_sequence
                #  The first new_len elements of both sequences in this case will represent the snake, and the last element
                #  will represent a single deletion.
                stack.append((current_x + new_len, current_y + new_len, old_len - new_len, 0))
            else:
                # (new_len == old_len) This reduces to a snake which does not contain any edits.
                pass

        elif old_len > 0 or new_len > 0:
            # Compute context indexes.
            hunk: Hunk = Hunk()
            hunk.start1 = max(0, current_x - ctx_len)
            hunk.start2 = max(0, current_y - ctx_len)

            mergable = len(trace) and hunk.start1 <= (trace[-1].start1 + trace[-1].length1)
            if mergable:
                hunk = trace.pop()
                ectx = hunk.diffs.pop()  # Remove trailing ctx
                last_pos = hunk.start1 + hunk.length1 - len(ectx[1])
                eq_len = current_x - last_pos
                if eq_len > 0:
                    hunk.diffs.append((EQ, old_sequence[last_pos:last_pos + eq_len]))

            elif current_x - hunk.start1 > 0:
                hunk.diffs.append((EQ, old_sequence[hunk.start1:current_x]))

            if old_len > 0:
                # Only Horizontal - Deletions.
                hunk.diffs.append((DL, old_sequence[current_x:current_x + old_len]))
            elif new_len > 0:
                # Only Vertical - Insertions.
                hunk.diffs.append((IN, new_sequence[current_y:current_y + new_len]))

            hunk.length1 = min(len(old_sequence), current_x + old_len + ctx_len) - hunk.start1
            hunk.length2 = min(len(new_sequence), current_y + new_len + ctx_len) - hunk.start2
            end_ctx_len = hunk.length1 - old_len - (current_x - hunk.start1)
            if end_ctx_len > 0:
                hunk.diffs.append(
                    (EQ, old_sequence[current_x + old_len:current_x + old_len + end_ctx_len]))

            trace.append(hunk)

    return trace


if __name__ == '__main__':
    # f1 = open(sys.argv[1]).read()
    # f2 = open(sys.argv[2]).read()

    f1 = open(sys.argv[1]).read().splitlines()
    f2 = open(sys.argv[2]).read().splitlines()

    diffs = shortest_edit_script(f1, f2, 3)

    for diff in diffs:
        print(diff, end='')
