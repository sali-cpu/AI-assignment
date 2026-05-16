import random
from collections import Counter

import chess
import chess.engine
from reconchess import Player
from reconchess.utilities import without_opponent_pieces, is_illegal_castle


class ImprovedAgent(Player):

    def __init__(self):
        self.board_states = set()
        self.color = None
        self.board = None

        self.engine = chess.engine.SimpleEngine.popen_uci(r'C:\Users\mbaye\Downloads\Assignment\stockfish-windows-x86-64-avx2\stockfish\stockfish-windows-x86-64-avx2.exe')

    def handle_game_start(self, color, board, opponent_name):
        self.color = color
        self.board = board.copy()
        self.board_states = {board.fen()}

    def handle_opponent_move_result(self, captured_my_piece, capture_square):
        next_states = set()

        for fen in self.board_states:
            board = chess.Board(fen)

            possible_moves = []

            possible_moves.append(chess.Move.null())

            for move in board.pseudo_legal_moves:
                possible_moves.append(move)

            temp_board = without_opponent_pieces(board)

            for move in temp_board.generate_castling_moves():
                if not is_illegal_castle(board, move):
                    possible_moves.append(move)

            for move in possible_moves:
                new_board = board.copy()

                try:
                    if move != chess.Move.null():
                        is_capture = new_board.is_capture(move)

                        if captured_my_piece:
                            if not is_capture:
                                continue

                            if move.to_square != capture_square:
                                continue
                        else:
                            if is_capture:
                                continue

                    new_board.push(move)
                    next_states.add(new_board.fen())

                except:
                    pass

        if len(next_states) > 10000:
            next_states = set(random.sample(list(next_states), 10000))

        self.board_states = next_states

    def choose_sense(self, sense_actions, move_actions, seconds_left):

        valid_squares = []

        for square in sense_actions:
            file = chess.square_file(square)
            rank = chess.square_rank(square)

            if 0 < file < 7 and 0 < rank < 7:
                valid_squares.append(square)

        uncertainty_scores = {}

        for square in valid_squares:
            observed = []

            for fen in self.board_states:
                board = chess.Board(fen)

                local_view = []

                center_file = chess.square_file(square)
                center_rank = chess.square_rank(square)

                for df in [-1, 0, 1]:
                    for dr in [-1, 0, 1]:
                        f = center_file + df
                        r = center_rank + dr

                        if 0 <= f <= 7 and 0 <= r <= 7:
                            sq = chess.square(f, r)
                            piece = board.piece_at(sq)

                            if piece:
                                local_view.append(piece.symbol())
                            else:
                                local_view.append('.')

                observed.append(tuple(local_view))

            uncertainty_scores[square] = len(set(observed))

        if uncertainty_scores:
            return max(uncertainty_scores, key=uncertainty_scores.get)

        return random.choice(valid_squares)

    def handle_sense_result(self, sense_result):

        filtered_states = set()

        for fen in self.board_states:
            board = chess.Board(fen)
            consistent = True

            for square, piece in sense_result:
                current_piece = board.piece_at(square)

                if piece is None:
                    if current_piece is not None:
                        consistent = False
                        break
                else:
                    if current_piece is None:
                        consistent = False
                        break

                    if current_piece.symbol() != piece.symbol():
                        consistent = False
                        break

            if consistent:
                filtered_states.add(fen)

        self.board_states = filtered_states

    def choose_move(self, move_actions, seconds_left):

        if len(self.board_states) == 0:
            return random.choice(move_actions)

        if len(self.board_states) > 10000:
            self.board_states = set(random.sample(list(self.board_states), 10000))

        moves = []

        time_limit = max(0.01, 10 / max(1, len(self.board_states)))

        for fen in self.board_states:
            board = chess.Board(fen)

            selected_move = None

            for move in board.pseudo_legal_moves:
                if board.is_capture(move):
                    captured_piece = board.piece_at(move.to_square)

                    if captured_piece and captured_piece.symbol().lower() == 'k':
                        selected_move = move
                        break

            if selected_move is None:
                try:
                    result = self.engine.play(
                        board,
                        chess.engine.Limit(time=time_limit)
                    )

                    selected_move = result.move

                except:
                    continue

            if selected_move in move_actions:
                moves.append(selected_move)

        if not moves:
            return random.choice(move_actions)

        counts = Counter(moves)
        best_count = max(counts.values())

        best_moves = [move for move in counts if counts[move] == best_count]

        return sorted(best_moves, key=lambda x: x.uci())[0]

    def handle_move_result(
        self,
        requested_move,
        taken_move,
        captured_opponent_piece,
        capture_square
    ):

        updated_states = set()

        for fen in self.board_states:
            board = chess.Board(fen)

            try:
                if taken_move is not None:
                    board.push(taken_move)
                else:
                    board.push(chess.Move.null())

                updated_states.add(board.fen())

            except:
                pass

        self.board_states = updated_states

    def handle_game_end(self, winner_color, win_reason, game_history):
        try:
            self.engine.quit()
        except:
            pass