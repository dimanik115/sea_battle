import random as r
from typing import List, Optional


class Ship:
    __slots__ = ('x', 'y', 'length', 'tp', 'broken_cells')

    def __init__(self, length: int, tp: int = 1, x: Optional[int] = None,
                 y: Optional[int] = None) -> None:
        self.length = length
        self.tp = tp
        self.x = x
        self.y = y
        self.broken_cells = [0 for i in range(length)]

    def get_start_coords(self):
        return self.x, self.y

    def set_start_coords(self, x: int, y: int):
        self.x = x
        self.y = y

    def __getitem__(self, index: int):
        return self.broken_cells[index]

    def __setitem__(self, index: int, value: int):
        self.broken_cells[index] = value

    def __str__(self) -> str:
        return f'({self.x}, {self.y}) leng={self.length} tp={self.tp}'


class GamePole:
    __slots__ = ('size', 'ships')

    def __init__(self, size: int = 10) -> None:
        self.size = size
        self.ships = [Ship(4, tp=r.randint(1, 2)), Ship(3, tp=r.randint(1, 2)), Ship(3, tp=r.randint(1, 2)),
                      Ship(2, tp=r.randint(1, 2)), Ship(2, tp=r.randint(1, 2)), Ship(2, tp=r.randint(1, 2)),
                      Ship(1, tp=r.randint(1, 2)), Ship(1, tp=r.randint(1, 2)), Ship(1, tp=r.randint(1, 2)),
                      Ship(1, tp=r.randint(1, 2))]
        self.make_coord()

    def get_pole(self):
        pole = [['!']*self.size for _ in range(self.size)]
        for ship in self.ships:
            for i in range(ship.length):
                if ship.tp == 1:
                    pole[ship.y][ship.x + i] = ship.broken_cells[i]
                elif ship.tp == 2:
                    pole[ship.y + i][ship.x] = ship.broken_cells[i]
        return pole

    def make_coord(self):
        dx = (-1, 0, 1, -1, 1, -1, 0, 1)
        dy = (-1, -1, -1, 0, 0, 1, 1, 1)
        pole = [[0]*(self.size + 2) for _ in range(self.size + 2)]
        for ship in self.ships:
            while True:
                flag = True
                x, y = r.randint(1, self.size), r.randint(1, self.size)
                L = ship.length
                if pole[y][x] != 0 or (x + L - 1 > self.size or y + L - 1 > self.size):
                    continue
                for k in range(L):
                    for i, j in zip(dx, dy):
                        if (ship.tp == 1 and pole[y + j][x + i + k] != 0) or\
                           (ship.tp == 2 and pole[y + j + k][x + i] != 0):
                            flag = False
                            break
                if not flag:
                    continue
                for i in range(ship.length):
                    if ship.tp == 1:
                        pole[y][x + i] = 1
                    elif ship.tp == 2:
                        pole[y + i][x] = 1
                ship.set_start_coords(x-1, y-1)
                break


class Battle:
    __slots__ = ('__player', '__bot')

    def __init__(self, pole=GamePole()) -> None:
        self.__player = pole
        self.__bot = GamePole(size=pole.size)

    def begin_game(self):
        """ корабль изображен - 0, сбитый корабль - 1, вода - !, выстрел мимо - \u00D7"""

        my_pole = self.__player.get_pole()
        opponent_pole = [['!']*self.__bot.size for _ in range(self.__bot.size)]
        bot_pole = [['!']*self.__bot.size for _ in range(self.__bot.size)]
        while True:
            while True:
                print('Введите, что вы хотите сделать:')
                print('1: показать свое поле')
                print('2: показать ячейки чужого поля')
                print('3: сделать ход')
                while True:
                    try:
                        step = int(input())
                        break
                    except ValueError:
                        print('Неверный ввод!')
                if step == 1:
                    for row in my_pole:
                        print(*row)
                elif step == 2:
                    for row in opponent_pole:
                        print(*row)
                elif step == 3:
                    while True:
                        cell = input(f'Введите 2 числа через пробел (0-{self.__bot.size - 1}): ').split()
                        try:
                            x, y = map(int, cell)
                            if opponent_pole[y][x] == '!':
                                self.change_pole(x, y, opponent_pole, self.__bot)
                                break
                            else:
                                print('Вы уже вводили эти значения!')
                        except (IndexError, ValueError):
                            print('Неверный ввод!')
                    break
            if all(all(i.broken_cells) for i in self.__bot.ships):
                print('Поздравляем, вы победили!')
                print('Ваше поле:')
                for row in my_pole:
                    print(*row)
                return
            # TODO улучшить интеллект бота:
            # если прошлый ход попал, то следующий ход основывать на прошлом, используя 4 возможных направления
            # если корабль потопил, то сразу убирать область вокруг него из возможных значений
            while True:
                x_b, y_b = r.randint(0, self.__bot.size - 1), r.randint(0, self.__bot.size - 1)
                if bot_pole[y_b][x_b] == '!':
                    self.change_pole(x_b, y_b, bot_pole, self.__player)
                    if my_pole[y_b][x_b] == '!':
                        my_pole[y_b][x_b] = '\u00D7'
                    else:
                        my_pole[y_b][x_b] = 1
                    break
            if all(all(i.broken_cells) for i in self.__player.ships):
                print('Бот победил(')
                print('Поле оппонента:')
                for row in opponent_pole:
                    print(*row)
                return

    @staticmethod
    def change_pole(x: int, y: int, pole: List[List[str]], side: GamePole):
        if side.get_pole()[y][x] == '!':
            pole[y][x] = '\u00D7'
        else:
            pole[y][x] = 1
            for i, ship in enumerate(side.ships):
                for j in range(ship.length):
                    if ship.tp == 1 and (x, y) == (ship.x + j, ship.y) or\
                       ship.tp == 2 and (x, y) == (ship.x, ship.y + j):
                        side.ships[i][j] = 1
                        return


if __name__ == '__main__':
    b = Battle()
    for row in b._Battle__bot.get_pole():
        print(*row)
    print()
    b.begin_game()
