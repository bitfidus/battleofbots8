import fileinput
from collections import defaultdict
from random import choice
import time


class Board(object):

    def __init__(self, lines):

        self.stones_by_player = defaultdict(list)
        self.occupied = dict()

        for x, line in enumerate(lines[:6]):
            for y, stone in enumerate(line.split(' ')):
                if stone == '0':
                    continue
                coor = (x, y)
                self.occupied[coor] = stone
                self.stones_by_player[stone].append(coor)

    @classmethod
    def copy(cls_, board):
        b = cls_([])
        b.stones_by_player = dict((x, y[:]) for x, y in board.stones_by_player.iteritems())
        b.occupied = dict(board.occupied)
        return b

    def eval(self, player):
        other_player = '1' if player == '2' else '2'
        return len(self.stones_by_player[player]) - len(self.stones_by_player[other_player])

    def spreading(self, move):
        """
        """
        from_, to = move
        player = self.occupied[from_]
        # self.stones_by_player[player] = [x0 for x0 in self.stones_by_player[player] if x0 != from_]
        self.stones_by_player[player].append(to)
        self.occupied[to] = player
        other_player = '1' if player == '2' else '2'
        adjacents = [x for x in self.adjacents(to) if x in self.stones_by_player[other_player]]
        for x in adjacents:
            self.occupied[x] = player
            self.stones_by_player[player].append(x)
            self.stones_by_player[other_player] = [x0 for x0 in self.stones_by_player[other_player] if x0 != x]

    def jumping(self, move):
        """
        """
        from_, to = move

        player = self.occupied[from_]
        self.occupied[to] = player
        other_player = '1' if player == '2' else '2'
        self.stones_by_player[player].append(to)
        adjacents = [x for x in self.adjacents(to) if x in self.stones_by_player[other_player]]
        for x in adjacents:
            self.occupied[x] = player
            self.stones_by_player[player].append(x)
            self.stones_by_player[other_player] = [x0 for x0 in self.stones_by_player[other_player] if x0 != x]

    @staticmethod
    def valid(coor):
        x, y = coor
        return x >= 0 and x < 6 and y >= 0 and y < 7

    @staticmethod
    def move(coor, offset):
        x, y = coor

        l = [
            (x, y - offset), (x - offset, y), (x, y +offset),
            (x + offset, y - offset), (x + offset, y), (x + offset, y + offset),
        ]
        return [item for item in l if Board.valid(item)]

    @staticmethod
    def adjacents(coor):
        x, y = coor
        yparity = (y & 1)
        rev_yparity = 0 if (y & 1) else 1
        l = [
            (x - 1 + yparity, y - 1), (x - 1, y), (x - 1 + yparity, y + 1),
            (x + 1 - rev_yparity, y - 1), (x + 1, y), (x + 1 - rev_yparity, y + 1),
        ]
        return [item for item in l if Board.valid(item)]

    @staticmethod
    def spreading_moves(coor):
        return [(coor, item) for item in Board.adjacents(coor)]

    @staticmethod
    def jumping_moves(coor):
        x, y = coor
        yparity = (y & 1)
        rev_yparity = 0 if (y & 1) else 1
        l = [
           #             (x - 2, y - 1), (x - 2, y + 1),
           (x - 1, y - 2), (x - 2, y), (x - 1, y + 2),
           (x + 1, y - 2), (x + 2, y), (x + 1, y + 2),
           #           (x + 2, y - 1), (x + 2, y + 1),
        ]
        l = [
            (x - 2, y),
            (x - 2 + yparity, y + 1),
            (x - 1, y + 2),
            (x, y + 2),
            (x + 1, y + 2),
            (x + 2 - rev_yparity, y + 1),
            (x + 2, y),
            (x + 2 - rev_yparity, y - 1),
            (x + 1, y - 2),
            (x, y - 2),
            (x - 1, y - 2),
            (x - 2 + yparity, y - 1)


        ]
        return [(coor, item) for item in l if Board.valid(item)]


    def get_valid_moves(self, player):
        """
        """
        spreading = list()
        jumping = list()
        for stone in self.stones_by_player[player]:
            spreading += Board.spreading_moves(stone)
            jumping += Board.jumping_moves(stone)
        # return [x for x in spreading if x not in self.occupied]
        return (
            [x for x in spreading if x[1] not in self.occupied],
            [x for x in jumping if x[1] not in self.occupied]
        )

MAX_DEEP = 10
TIME_LIMIT = 3

def play(turn, board, whoami, deep=0, t=None):
    other_player = '1' if whoami == '2' else '2'
    if deep > MAX_DEEP:
        return
    if not t:
        t = time.time()
    elif time.time() - t > TIME_LIMIT:
        # print 'time', deep, time.time() - t
        return
    spreading, jumping = board.get_valid_moves(whoami)
    if turn < 6:
        jumping = []
    points = list()
    # spreading = [((4, 6), (3, 6))]
    # spreading = []
    for move in spreading:
        b = Board.copy(board)
        b.spreading(move)
        m = b.eval(whoami)
        # print '+' * (deep + 1), m, move
        m1 = play(turn + 1, b, other_player, deep + 1, t)
        if m1 is not None:
            m -= m1[0]
        points.append((m, move))
    # jumping = [((4, 1), (5, 3))]
    for move in jumping:
        b = Board.copy(board)
        b.jumping(move)
        m = b.eval(whoami)
        # print '*' * (deep + 1), m, move
        m1 = play(turn + 1, b, other_player, deep + 1, t)
        if m1 is not None:
            m -= m1[0]
        points.append((m, move))

        # points.append((b.eval(whoami), move))
    if not points:
        # No tiene movimientos, peor puntuacion
        return (-999, None)
    # if deep == 0:
    #     print sorted(points, key=lambda x: x[0], reverse=True)
    max_move = max(points, key=lambda x: x[0])
    # import pprint
    # pprint.pprint(points)
    # print max_move
    return max_move


def main():
    lines = [x.strip() for x in fileinput.input()]
    b = Board(lines)
    turn = int(lines[-2])
    whoami = lines[-1]
    # print [x[1] for x in Board.jumping_moves((2, 2))]
    # print [x[1] for x in Board.jumping_moves((2, 3))]
    # print [x[1] for x in Board.jumping_moves((2, 5))]
    # return
    move = play(turn, b, whoami)[1]

    print ' '.join(str(x) for x in move[0])
    print ' '.join(str(x) for x in move[1])




if __name__ == '__main__':
    main()





