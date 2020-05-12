import socket
import pygame

WIDTH = 750
HEIGHT = 390


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

done = False

crossImg = pygame.image.load('img/cross.png')
shipImg = pygame.image.load('img/ship_self.png')

########### GAME

class Game():

    #active player
    #0 - player 1
    #1 - player 2

    # Stages:
    # 1. Picking place for our ships

    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.active_player = 0
        self.ships = {
            4: 1,
            3: 2,
            2: 3,
            1: 5
        }

    def start_conf(self):
        self.players[self.active_player].is_active = 1

    def draw_boards(self):
        for player in self.players:
            player.draw_all()

    def place_ship_phase(self):
        for player in self.players:
            player.game_phase = 1
            for ship_size, ship_number in self.ships.items():
                for ship in ship_number:
                    player.place_ship_structure(ship_size)

    def change_turns(self):
        self.players[self.active_player].is_active = 0
        self.active_player = not self.active_player
        self.players[self.active_player].is_active = 1




########### PLAYER

class Player():

    # Player_num
    # 0 is left
    # 1 is right side of the screen

    # Game Phases
    # 1 is placing ships
    # 2 is attacking enemy ships

    def __init__(self, player_num):
        self.player_num = player_num
        self.board = Board(player_num)
        self.picked_square_in_width = 0
        self.picked_square_in_height = 0
        self.ships_places = []
        self.is_active = 0
        self.game_phase = 1
        self.placed_ship_started = 0
        self.next_ship_size = 0

    def change_picked_square(self, width, height):
        if self.picked_square_in_width + width >= 0 and self.picked_square_in_width + width < self.board.dimension:
            self.picked_square_in_width = self.picked_square_in_width + width
        if self.picked_square_in_height + height >= 0 and self.picked_square_in_height + height < self.board.dimension:
            self.picked_square_in_height = self.picked_square_in_height + height
        self.draw_border()

    def check_if_can_place_ship(self, is_placing_started, whole_ship_position = []):
        can_place = True
        if is_placing_started == 0:
            for ship in self.ships_places:
                if ship[0] == self.picked_square_in_width - 1 and ship[1] == self.picked_square_in_height - 1:
                    can_place = False
                elif ship[0] == self.picked_square_in_width and ship[1] == self.picked_square_in_height - 1:
                    can_place = False
                elif ship[0] == self.picked_square_in_width + 1 and ship[1] == self.picked_square_in_height - 1:
                    can_place = False
                elif ship[0] == self.picked_square_in_width - 1 and ship[1] == self.picked_square_in_height:
                    can_place = False
                elif ship[0] == self.picked_square_in_width and ship[1] == self.picked_square_in_height:
                    can_place = False
                elif ship[0] == self.picked_square_in_width + 1 and ship[1] == self.picked_square_in_height:
                    can_place = False
                elif ship[0] == self.picked_square_in_width - 1 and ship[1] == self.picked_square_in_height + 1:
                    can_place = False
                elif ship[0] == self.picked_square_in_width and ship[1] == self.picked_square_in_height + 1:
                    can_place = False
                elif ship[0] == self.picked_square_in_width + 1  and ship[1] == self.picked_square_in_height + 1:
                    can_place = False

        return can_place


    def draw_board(self):
        self.board.draw_board()

    def draw_ships(self):
        self.board.draw_ships(self.ships_places)

    def draw_border(self):
        if self.game_phase == 1:
            can_place = self.check_if_can_place_ship(0)
            self.board.draw_border(self.picked_square_in_width, self.picked_square_in_height, can_place)

    def draw_cross(self):
        self.board.draw_img(crossImg ,self.picked_square_in_width, self.picked_square_in_height)

    def draw_ship(self):
        self.board.draw_img(shipImg, self.picked_square_in_width, self.picked_square_in_height)

    def place_ship(self):
        placed = 0

        can_place = self.check_if_can_place_ship(0)
        if can_place:
            self.ships_places.append([self.picked_square_in_width, self.picked_square_in_height])



    def draw_all(self):

        if self.is_active:
            self.draw_border_on_self()
        self.draw_board()
        self.draw_ships()
############# BOARD

class Board():

    def __init__(self, player_num):

        # Drawing specs

        self.dimension = 10
        self.square_width = 22
        self.square_height = 22
        self.spacing_between = 6
        self.border_size = 3
        self.player_num = player_num

        # Ships info

        self.ships_postion = []
        self.shots_hit_position = []
        self.shots_missed_position = []



    def draw_board(self):
        for square_num_width in range(self.dimension):
            for square_num_height in range(self.dimension):

                square_x_pos = 50 + ( (WIDTH / 2) * self.player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
                square_y_pos = 30 + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

                pygame.draw.rect(screen, (255, 255, 255), (square_x_pos, square_y_pos, self.square_width, self.square_height))

    def draw_ships(self, ships_places):
        for ship in ships_places:
            for square_num_width in range(self.dimension):
                for square_num_height in range(self.dimension):
                    if ship[0] == square_num_width and ship[1] == square_num_height:
                        self.draw_img(shipImg, square_num_width, square_num_height)

    def draw_border(self, sq_width_num, sq_height_num, valid):

        color = (255, 0, 0)

        if valid is True:
            color = (0, 255, 0)

        square_num_width = sq_width_num
        square_num_height = sq_height_num

        square_x_pos = 50 + ( (WIDTH / 2) * self.player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width)) - self.border_size
        square_y_pos = 30 + (22 * (square_num_height)) + (self.spacing_between * (square_num_height)) - self.border_size

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        pygame.draw.rect(screen, color, (square_x_pos, square_y_pos, square_width, square_height))

    def draw_action(self, img, sq_width_num, sq_height_num):

        square_num_width = sq_width_num
        square_num_height = sq_height_num

        square_x_pos = 50 + ( (WIDTH / 2) * self.player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
        square_y_pos = 30 + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        screen.blit(img, (square_x_pos,square_y_pos))




player1 = Player(0)
player2 = Player(1)

game = Game(player1, player2)
game.start_conf()


while not done:

    screen.fill((0,0,0))

    active_player = game.players[game.active_player]
    active_player.draw_border_on_self()

    game.draw_boards()

    active_player.draw_ship()

    for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        active_player.change_picked_square(0, 1)
                    elif event.key == pygame.K_LEFT:
                        active_player.change_picked_square(-1, 0)
                    elif event.key == pygame.K_UP:
                        active_player.change_picked_square(0, -1)
                    elif event.key == pygame.K_RIGHT:
                        active_player.change_picked_square(1, 0)
                    elif event.key == pygame.K_RETURN:
                        active_player.place_ship()
                    elif event.key == pygame.K_SPACE:
                        game.change_turns()

    pygame.display.flip()
