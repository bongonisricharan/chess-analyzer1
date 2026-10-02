"""Chess engine: move generation, evaluation and plain minimax (no pruning).

The board is an 8x8 list of lists. Rows go from rank 8 (index 0) down to
rank 1 (index 7). Uppercase letters are White, lowercase are Black,
None is an empty square.
"""

VALUES = {"p": 1, "n": 3, "b": 3, "r": 5, "q": 9, "k": 100}
SEARCH_DEPTH = 3

INITIAL_BOARD = [
    list("rnbqkbnr"),
    list("pppppppp"),
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    list("PPPPPPPP"),
    list("RNBQKBNR"),
]

KNIGHT_JUMPS = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)]
DIAGONALS = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
STRAIGHTS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def square_name(r, c):
    """(row, col) -> chess notation, e.g. (6, 4) -> 'e2'."""
    return chr(ord("a") + c) + str(8 - r)


def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


def same_color(a, b):
    return a is not None and b is not None and a.isupper() == b.isupper()


def sliding_moves(board, r, c, directions):
    piece = board[r][c]
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[nr][nc] is None:
                moves.append((nr, nc))
            else:
                if not same_color(piece, board[nr][nc]):
                    moves.append((nr, nc))
                break
            nr += dr
            nc += dc
    return moves


def get_moves(board, r, c):
    """All pseudo-legal destination squares for the piece at (r, c)."""
    piece = board[r][c]
    if piece is None:
        return []

    white = piece.isupper()
    kind = piece.lower()
    moves = []

    if kind == "p":
        direction = -1 if white else 1
        start_row = 6 if white else 1
        one = r + direction
        if in_bounds(one, c) and board[one][c] is None:
            moves.append((one, c))
            two = r + 2 * direction
            if r == start_row and board[two][c] is None:
                moves.append((two, c))
        for dc in (-1, 1):
            nr, nc = r + direction, c + dc
            if (in_bounds(nr, nc) and board[nr][nc] is not None
                    and not same_color(piece, board[nr][nc])):
                moves.append((nr, nc))

    elif kind == "n":
        for dr, dc in KNIGHT_JUMPS:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and not same_color(piece, board[nr][nc]):
                moves.append((nr, nc))

    elif kind == "b":
        moves.extend(sliding_moves(board, r, c, DIAGONALS))

    elif kind == "r":
        moves.extend(sliding_moves(board, r, c, STRAIGHTS))

    elif kind == "q":
        moves.extend(sliding_moves(board, r, c, DIAGONALS + STRAIGHTS))

    elif kind == "k":
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc) and not same_color(piece, board[nr][nc]):
                    moves.append((nr, nc))

    return moves


def make_move(board, frm, to):
    """Return a new board with the move played (pawns auto-promote to queens)."""
    new_board = [row[:] for row in board]
    piece = new_board[frm[0]][frm[1]]
    if piece == "P" and to[0] == 0:
        piece = "Q"
    if piece == "p" and to[0] == 7:
        piece = "q"
    new_board[to[0]][to[1]] = piece
    new_board[frm[0]][frm[1]] = None
    return new_board


def evaluate(board):
    """Material score (White - Black) plus a tiny bonus for central pieces."""
    score = 0.0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece is None:
                continue
            kind = piece.lower()
            value = VALUES[kind]
            if kind != "k":
                centre = 3.5 - max(abs(r - 3.5), abs(c - 3.5)) + 0.5
                value += 0.03 * centre
            score += value if piece.isupper() else -value
    return score


def get_all_moves(board, white_turn):
    result = []
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece is not None and piece.isupper() == white_turn:
                for to in get_moves(board, r, c):
                    result.append(((r, c), to))
    return result


def minimax(board, depth, white_turn):
    """Plain minimax. White maximizes, Black minimizes."""
    if depth == 0:
        return evaluate(board)

    moves = get_all_moves(board, white_turn)
    if not moves:
        return evaluate(board)

    if white_turn:
        best = float("-inf")
        for frm, to in moves:
            best = max(best, minimax(make_move(board, frm, to), depth - 1, False))
        return best

    best = float("inf")
    for frm, to in moves:
        best = min(best, minimax(make_move(board, frm, to), depth - 1, True))
    return best


def get_best_move(board, white_turn, depth=SEARCH_DEPTH):
    """Return ((from_r, from_c), (to_r, to_c)) and its score, or None if no moves."""
    moves = get_all_moves(board, white_turn)
    if not moves:
        return None

    best_move = None
    best_score = float("-inf") if white_turn else float("inf")

    for frm, to in moves:
        score = minimax(make_move(board, frm, to), depth - 1, not white_turn)
        if (white_turn and score > best_score) or (not white_turn and score < best_score):
            best_score = score
            best_move = (frm, to)

    return best_move, best_score
