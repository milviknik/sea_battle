from random import randint

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        # Переопределение метода сравнения для точек
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        # Переопределение метода вывода для точек
        return f"({self.x}, {self.y})"

class BoardException(Exception):
    # Базовый класс для исключений на доске
    pass

class BoardOutException(BoardException):
    def __str__(self):
        # Исключение при выстреле за пределы доски
        return "Вы пытаетесь выстрелить за доску!"

class BoardUsedException(BoardException):
    def __str__(self):
        # Исключение при повторном выстреле в ту же клетку
        return "Вы уже стреляли в эту клетку"

class BoardWrongShipException(BoardException):
    # Исключение при неправильном расположении корабля на доске
    pass


class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow  # Координаты носа корабля
        self.l = l  # Длина корабля
        self.o = o  # Ориентация корабля (0 - горизонтально, 1 - вертикально)
        self.lives = l  # Количество жизней корабля равно его длине

    @property
    def dots(self):
        # Метод возвращает список точек, которые занимает корабль на доске
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        # Метод возвращает True если выстрел попал в корабль и False если мимо
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size  # размер доски
        self.hid = hid  # скрыть или нет доску

        self.count = 0  # количество сделанных выстрелов

        # создание двумерного списка для представления доски со всеми элементами инициализированными как "O"
        self.field = [["O"] * size for _ in range(size)]

        self.busy = []  # список занятых клеток
        self.ships = []  # список кораблей

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()  # вызов исключения при попытке добавить корабль в занятую клетку
        for d in ship.dots:
            self.field[d.x][d.y] = "■"  # добавление корабля на доску
            self.busy.append(d)  # добавление координат корабля в список занятых клеток

        self.ships.append(ship)  # добавление корабля в список кораблей
        self.contour(ship)  # вызов метода contour для обозначения контура вокруг корабля

    def contour(self, ship, verb = False):
        # список смещений для определения клеток вокруг корабля
        near = [
            (-1, -1), (-1, 0) , (-1, 1),
            (0, -1), (0, 0) , (0 , 1),
            (1, -1), (1, 0) , (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                # если клетка не выходит за пределы доски и не занята
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "." # обозначение контура вокруг корабля
                    self.busy.append(cur) # добавление клетки в список занятых

    def __str__(self):
        res = ""
        # создание строки с номерами столбцов
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            # добавление номера строки и элементов строки в res
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            # замена символа корабля на символ пустой клетки если доска скрыта
            res = res.replace("■", "O")
        return res

    def out(self, d):
        # проверка выходит ли точка d за пределы доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()  # вызов исключения если выстрел сделан за пределами доски

        if d in self.busy:
            raise BoardUsedException()  # вызов исключения если выстрел сделан в занятую клетку

        self.busy.append(d)  # добавление координат выстрела в список занятых клеток

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1  # уменьшение количества жизней корабля
                self.field[d.x][d.y] = "X"  # обозначение попадания на доске
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."  # обозначение промаха на доске
        print("Мимо!")  # сообщение о промахе
        return False

    def begin(self):
        self.busy = []  # очистка списка занятых клеток перед началом игры


class Player:
    def __init__(self, board, enemy):
        self.board = board  # доска игрока
        self.enemy = enemy  # доска противника

    def ask(self):
        raise NotImplementedError()  # метод должен быть реализован в дочерних классах

    def move(self):
        while True:
            try:
                target = self.ask()  # получение координат выстрела
                repeat = self.enemy.shot(target)  # выполнение выстрела по противнику
                return repeat
            except BoardException as e:
                print(e)  # обработка исключений при выстреле


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))  # генерация случайных координат выстрела
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()  # ввод координат выстрела пользователем

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)  # возврат объекта Dot с координатами выстрела


class Game:
    def __init__(self, size=6):
        self.size = size  # размер игрового поля
        pl = self.random_board()  # создание случайного игрового поля для игрока
        co = self.random_board()  # создание случайного игрового поля для компьютера
        co.hid = True  # скрытие кораблей компьютера

        self.ai = AI(co, pl)  # создание искусственного интеллекта для компьютера
        self.us = User(pl, co)  # создание пользователя

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()  # расстановка кораблей на доске случайным образом
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # длины кораблей
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l,
                            randint(0, 1))  # создание корабля со случайными координатами и направлением
                try:
                    board.add_ship(ship)  # добавление корабля на доску
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print(" Приветствуем вас ")
        print(" в игре ")
        print(" морской бой ")
        print("-------------------")

    def loop(self):
        num = 0  # счетчик ходов
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)  # вывод игрового поля пользователя
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)  # вывод игрового поля компьютера
            if num % 2 == 0:  # если номер хода четный
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()  # ход пользователя
            else:  # если номер хода нечетный
                print("-" * 20)
                print("Ходит компьютер!")
                repeat = self.ai.move()  # ход компьютера
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()  # приветствие игрока
        self.loop()  # запуск игрового цикла

g = Game()  # создание объекта класса Game
g.start()  # запуск игры