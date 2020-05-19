import socket
import pygame
from network import Network
from utilities import find_left_ship, find_right_ship, find_lowest_ship, find_highest_ship

WIDTH = 750
HEIGHT = 390


########### Images

crossImg = pygame.image.load('img/cross.png')
shipImg = pygame.image.load('img/ship_self.png')
missedShot = pygame.image.load('img/shotMissed.png')
shipKilled = pygame.image.load('img/shipKilled.png')

########### Colors

color_red = (255, 0, 0)
color_green = (0, 255, 0)


class Player():

    def __init__(self, player_num, canvas, game):
        self.width_position = 0
        self.height_position = 0
        self.is_active = 0
        self.player_num = player_num
        self.canvas = canvas
        self.game = game

    def draw_position(self):
        self.canvas.draw_position()

    def change_position(self, width, height):
        if self.width_position + width >= 0 and self.width_position + width < 10:
            self.width_position = self.width_position + width
        if self.height_position + height >= 0 and self.height_position + height < 10:
            self.height_position = self.height_position + height
        self.canvas.change_player_position(self.width_position, self.height_position)


    def make_action(self, game_phase):
        if game_phase == 1:
            self.place_ship()
        elif game_phase == 3:
            self.place_attack()


    def place_ship(self):
        self.canvas.place_ship()

    def place_attack(self):
        result = self.canvas.place_attack()
        if result != [-1, -1]:
            #self.game.check_if_hit(result[0], result[1])
            self.game.change_turn(result[0], result[1])

class Game():

    def __init__(self):
        self.net = Network()
        self.canvas = Canvas(WIDTH, HEIGHT, "Stateczki", self.net.id)
        self.player = Player(self.net.id, self.canvas, self)
        self.player2 = Player(1 - self.net.id, self.canvas, self)
        self.is_player_active = self.set_start_active_state()
        self.game_phase = 1

    def set_start_active_state(self):
        if self.net.is_player_active == 1:
            self.player.is_active = 1
            return 1
        else:
            self.player.is_active = 0
            return 0

    def run(self):
        run = True
        pygame.init()
        while run:

            action_num = 0 #Default is 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.K_ESCAPE:
                    run = False

                if event.type == pygame.KEYDOWN:

                    keys = pygame.key.get_pressed()

                    if self.is_player_active:

                        if keys[pygame.K_RIGHT]:
                            self.player.change_position(1, 0)

                        if keys[pygame.K_LEFT]:
                            self.player.change_position(-1, 0)

                        if keys[pygame.K_UP]:
                            self.player.change_position(0, -1)

                        if keys[pygame.K_DOWN]:
                            self.player.change_position(0, 1)

                        if keys[pygame.K_RETURN]:
                            self.player.make_action(self.game_phase)

            if self.game_phase == 1:
                player_num, game_phase = self.parse_data(self.send_data(0))

                player_num = int(player_num)
                game_phase = int(game_phase)

                if self.canvas.first_phase_ended():
                    self.change_game_phase(2)

            elif self.game_phase == 2:
                player_num, game_phase = self.parse_data(self.send_data(0))

                player_num = int(player_num)
                game_phase = int(game_phase)

                if game_phase == 3:
                    self.change_game_phase(3)

            elif self.game_phase == 3:
                #Battle
                active_player_num, game_phase, returned_action_num, player_width, player_height = self.parse_data(self.send_data(action_num))

                active_player_num = int(active_player_num)
                game_phase = int(game_phase)
                returned_action_num = int(returned_action_num)
                player_width = int(player_width)
                player_height = int(player_height)

                self.canvas.set_active_player_coords(player_width, player_height)
                self.set_active_player(active_player_num)




            self.canvas.change_active_player(self.active_player_num())
            self.canvas.update()

    def check_if_hit(self, w, h):
        active_player_num, game_phase, returned_action_num, player_width, player_height = self.parse_data(self.send_data(2))



    def change_turn(self, w, h):
        active_player_num, game_phase, returned_action_num, player_width, player_height = self.parse_data(self.send_data(1))

        self.set_active_player(active_player_num)
        self.canvas.change_active_player(self.active_player_num())




    def change_game_phase(self, game_phase):
        self.game_phase = game_phase
        self.canvas.change_game_phase(game_phase)

    def draw_position(self):
        if self.is_player_active == 1:
            self.player.draw_position()
        else:
            self.player2.width_position = player_width
            self.player2.height_position = player_height
            self.player2.draw_position()


    def send_data(self, action):
        player_num, w, h = self.active_player_info()
        data = ""
        if self.is_player_active == 0:
            print("Nieaktywny")
            data = f'{player_num}:{self.game_phase}:-1:{w}:{h}'
        else:
            print("Aktywny")
            data = f'{player_num}:{self.game_phase}:{action}:{w}:{h}'
        reply = self.net.send(data)
        print("REPLY:" + reply)
        return reply

    @staticmethod
    def parse_data(data):
        try:
            d = data.split(":")
            return d
        except:
            return 0,0

    def active_player_info(self):
        active_player_id = 0

        if self.is_player_active == 1:
            active_player_id = self.net.id
        else:
            active_player_id = 1 - self.net.id

        return active_player_id, self.player.width_position, self.player.height_position

    def active_player_num(self):
        if self.is_player_active == 1:
            return self.player.player_num
        else:
            return self.player2.player_num

    def set_active_player(self, num):
        if num == self.net.id:
            self.is_player_active = 1
        else:
            self.is_player_active = 0





class Canvas():

    def __init__(self, w, h, name, player_id):
        self.width = w
        self.height = h
        self.screen = pygame.display.set_mode((w, h))
        self.board1 = Board(0, self.screen)
        self.board2 = Board(1, self.screen)
        self.game_phase = 1
        self.active_player_num = 0
        self.player_id = player_id
        self.active_player_w = 0
        self.active_player_h = 0
        pygame.display.set_caption(name)


    def change_active_player(self, active_player_num):
        self.active_player_num = active_player_num

    def update(self):
        self.draw_all()
        pygame.display.update()

    def draw_background(self):
        self.screen.fill((0, 0, 0))

    def get_canvas(self):
        return self

    def draw_boards(self):
        self.board1.draw_board()
        self.board2.draw_board()

    def draw_position(self):
        if self.active_player_num == 0:
            self.board1.draw_position()
        if self.active_player_num == 1:
            self.board2.draw_position()

    def draw_position_on_enemy(self):
        if self.active_player_num == 1:
            self.board1.draw_position()
        if self.active_player_num == 0:
            self.board2.draw_position()

    def draw_position_current_player(self):
        #Maluj na przeciwnika
        if self.active_player_num == self.player_id:
            if self.active_player_num == 0:
                self.board2.draw_position_on_coords(self.active_player_w, self.active_player_h)
            elif self.active_player_num == 1:
                self.board1.draw_position_on_coords(self.active_player_w, self.active_player_h)
        #Maluj u siebie
        elif self.active_player_num != self.player_id:
            if self.active_player_num == 1:
                self.board1.draw_position_on_coords(self.active_player_w, self.active_player_h)
            elif self.active_player_num == 0:
                self.board2.draw_position_on_coords(self.active_player_w, self.active_player_h)


    def draw_ship(self):
        if self.player_id == 0:
            self.board1.draw_ship()
        if self.player_id == 1:
            self.board2.draw_ship()

    def draw_ships(self):
        if self.player_id == 0:
            self.board1.draw_ships()
        if self.player_id == 1:
            self.board2.draw_ships()

    def draw_enemy_ships_killed(self):
        if self.player_id == 0:
            self.board2.draw_hits_succesful()
        if self.player_id == 1:
            self.board1.draw_hits_succesful()

    def draw_main_text(self, text):
        self.board1.draw_main_text(text)

    def draw_all(self):
        if self.game_phase == 1:
            self.draw_background()
            self.draw_position()
            self.draw_boards()
            self.draw_ship()
            self.draw_ships()

        elif self.game_phase == 2:
            self.draw_background()
            self.draw_position()
            self.draw_boards()
            self.draw_ships()
            self.draw_main_text("POCZEKAJ AŻ DRUGI GRACZ ROZSTAWI")

        elif self.game_phase == 3:
            self.draw_background()
            self.draw_position_current_player()
            self.draw_boards()
            self.draw_ships()
            self.draw_main_text("GRAMY")


    def first_phase_ended(self):
        if self.active_player_num == 0:
            return self.board1.placed_ships_figure == len(self.board1.ship_sizes)
        elif self.active_player_num == 1:
            return self.board2.placed_ships_figure == len(self.board2.ship_sizes)

    def change_game_phase(self, game_phase):
        self.game_phase = game_phase
        self.board1.game_phase = game_phase
        self.board2.game_phase = game_phase

    def change_player_position(self, w, h):
        if self.active_player_num == 0:
            self.board1.change_player_position(w, h)
        if self.active_player_num == 1:
            self.board2.change_player_position(w, h)

    def check_if_hit(self, w, h):
        if self.player_id == 0:
            return self.board1.check_if_hit(w, h)
        elif self.player_id == 1:
            return self.board2.check_if_hit(w, h)

    def set_active_player_coords(self, w, h):
        self.active_player_w = w
        self.active_player_h = h

    def place_ship(self):
        if self.active_player_num == 0:
            self.board1.place_ship()
        if self.active_player_num == 1:
            self.board2.place_ship()

    def place_attack(self):
        if self.active_player_num == 0:
            return self.board1.place_attack()
        if self.active_player_num == 1:
            return self.board2.place_attack()

    def hit_succesful(self, w, h):
        if self.active_player_num == 0:
            self.board1.hit_succesful(w, h)
            self.board2.enemy_hit_succesful(w, h)
        if self.active_player_num == 1:
            self.board2.hit_succesful(w, h)
            self.board1.enemy_hit_succesful(w, h)

    def hit_missed(self, w, h):
        if self.active_player_num == 0:
            self.board1.hit_missed(w, h)
            self.board2.enemy_hit_missed(w, h)
        if self.active_player_num == 1:
            self.board2.hit_missed(w, h)
            self.board1.enemy_hit_missed(w, h)

class Board():

    def __init__(self, board_num, screen):

        #Drawing parameters

        self.dimension = 10
        self.square_width = 22
        self.square_height = 22
        self.spacing_between = 6
        self.border_size = 3
        self.padding_top = 60

        self.board_num = board_num
        self.screen = screen
        self.game_phase = 1

        self.player_w = 0
        self.player_h = 0

        #Ships info

        self.ships = []
        self.current_ship_position = []
        self.placed_ships = 0
        self.placed_ships_figure = 0
        self.is_ship_being_placed = False
        self.ship_sizes = [2,1]
        self.shots_hit_position = []
        self.shots_missed_position = []
        self.enemy_hit_position = []
        self.enemy_missed_position = []

    def hit_succesful(self, w, h):
        self.shots_hit_position.append(w, h)

    def hit_missed(self, w, h):
        self.shots_missed_position.append(w, h)

    def enemy_hit_succesful(self, w, h):
        self.enemy_hit_position.append(w, h)

    def enemy_hit_missed(self, w, h):
        self.enemy_missed_position.append(w, h)

    def check_if_hit(self, w, h):
        if [w, h] in self.ships:
            return True
        else:
            return False


    def change_player_position(self, w, h):
        self.player_w = w
        self.player_h = h

    def draw_board(self):
        for square_num_width in range(self.dimension):
            for square_num_height in range(self.dimension):

                square_x_pos = 50 + ( (WIDTH / 2) * self.board_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
                square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

                pygame.draw.rect(self.screen, (255, 255, 255), (square_x_pos, square_y_pos, self.square_width, self.square_height))


    def draw_position(self):

        square_x_pos = 50 + ( (WIDTH / 2) * self.board_num) + (22 * (self.player_w)) + (self.spacing_between * (self.player_w)) - self.border_size
        square_y_pos = self.padding_top + (22 * (self.player_h)) + (self.spacing_between * (self.player_h)) - self.border_size

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        pygame.draw.rect(self.screen, self.border_color(), (square_x_pos, square_y_pos, square_width, square_height))

    def draw_position_on_coords(self, w, h):

        square_x_pos = 50 + ( (WIDTH / 2) * self.board_num) + (22 * (w)) + (self.spacing_between * (w)) - self.border_size
        square_y_pos = self.padding_top + (22 * (h)) + (self.spacing_between * (h)) - self.border_size

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        pygame.draw.rect(self.screen, self.border_color(), (square_x_pos, square_y_pos, square_width, square_height))

    def draw_action(self, img):

        square_x_pos = 50 + ( (WIDTH / 2) * self.board_num ) + (22 * (self.player_w)) + (self.spacing_between * (self.player_w))
        square_y_pos = self.padding_top + (22 * (self.player_h)) + (self.spacing_between * (self.player_h))

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        self.screen.blit(img, (square_x_pos,square_y_pos))

    def draw_ship(self):
        self.draw_action(shipImg)

    def draw_cross(self):
        self.draw_action(crossImg)

    def draw_missedShot(self):
        self.draw_action(missedShot)

    def draw_shipKilled(self):
        self.draw_action(shipKilled)


    def draw_icons_on_map(self, img, array):
        for item in array:
            for w in range(self.dimension):
                for h in range(self.dimension):
                    if item[0] == w and item[1] == h:
                        self.draw_item_on_map(img, w, h)

    def draw_item_on_map(self, img, w, h):

        square_x_pos = 50 + ( (WIDTH / 2) * self.board_num ) + (22 * (w)) + (self.spacing_between * (w))
        square_y_pos = self.padding_top + (22 * (h)) + (self.spacing_between * (h))

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        self.screen.blit(img, (square_x_pos,square_y_pos))

    def draw_ships(self):
        self.draw_icons_on_map(shipImg, self.ships)

    def draw_hits_succesful(self):
        self.draw_icons_on_map(shipKilled, self.shots_hit_position)


    def draw_main_text(self, text):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(text, True, (255,255,255), (0,0,0))
        textRect = text.get_rect()
        textRect.center = (WIDTH / 2, self.padding_top / 2)
        self.screen.blit(text, textRect)

    def draw_player_info_text(self, text):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(text, True, (255,255,255), (0,0,0))
        textRect = text.get_rect()
        if self.board_num == 0:
            textRect.center = (WIDTH / 4, HEIGHT - 30)
        elif self.board_num == 1:
            textRect.center = (3 * WIDTH / 4, HEIGHT - 30)
        screen.blit(text, textRect)

    def place_ship(self):
        if self.check_if_ship_place_is_valid():
            self.ships.append([self.player_w, self.player_h])
            self.current_ship_position.append([self.player_w, self.player_h])
            self.is_ship_being_placed = True
            self.placed_ships += 1

            if self.placed_ships == self.ship_sizes[self.placed_ships_figure]:
                self.is_ship_being_placed = False
                self.placed_ships = 0
                self.placed_ships_figure += 1
                self.current_ship_position = []

    def place_attack(self):
        if self.check_if_attack_is_valid():
            return self.player_w, self.player_h
        else:
            return [-1, -1]

    def border_color(self):
        if self.game_phase == 1:
            if self.check_if_ship_place_is_valid():
                return color_green
            else:
                return color_red
        elif self.game_phase == 2:
            return color_red
        elif self.game_phase == 3:
            if self.check_if_attack_is_valid():
                return color_green
            else:
                return color_red


    def check_if_attack_is_valid(self):
        if [self.player_w, self.player_h] in self.shots_missed_position or [self.player_w, self.player_h] in self.shots_hit_position:
            return False
        return True

    def check_if_ship_place_is_valid(self):

        # Jak to jest pierwszy statek z grupy
        # Tu sprawdzamy czy jakiś statek jest dookoła, albo na wybranym polu
        if self.is_ship_being_placed == False:
            can_place = True
            for ship in self.ships:
                if ship[0] == self.player_w - 1 and ship[1] == self.player_h - 1:
                    can_place = False
                elif ship[0] == self.player_w and ship[1] == self.player_h - 1:
                    can_place = False
                elif ship[0] == self.player_w + 1 and ship[1] == self.player_h - 1:
                    can_place = False
                elif ship[0] == self.player_w - 1 and ship[1] == self.player_h:
                    can_place = False
                elif ship[0] == self.player_w and ship[1] == self.player_h:
                    can_place = False
                elif ship[0] == self.player_w + 1 and ship[1] == self.player_h:
                    can_place = False
                elif ship[0] == self.player_w - 1 and ship[1] == self.player_h + 1:
                    can_place = False
                elif ship[0] == self.player_w and ship[1] == self.player_h + 1:
                    can_place = False
                elif ship[0] == self.player_w + 1  and ship[1] == self.player_h + 1:
                    can_place = False

        elif self.is_ship_being_placed == True:
            can_place = False

            if self.placed_ships == 1:

                can_place = True


                for placed_ship in self.ships:
                    for ship in self.current_ship_position:
                        # Tutaj wykluczamy stawianie na skosach

                        if ship[0] == self.player_w and ship[1] == self.player_h:
                            can_place = False
                        elif ship[0] == self.player_w - 1 and ship[1] == self.player_h - 1:
                            can_place = False
                        elif ship[0] == self.player_w + 1 and ship[1] == self.player_h + 1:
                            can_place = False
                        elif ship[0] == self.player_w - 1 and ship[1] == self.player_h + 1:
                            can_place = False
                        elif ship[0] == self.player_w + 1 and ship[1] == self.player_h - 1:
                            can_place = False
                        elif abs(ship[0] - self.player_w) > 1 or abs(ship[1] - self.player_h) > 1:
                            can_place = False

            elif self.placed_ships > 1:

                first_ship = self.current_ship_position[0]
                last_ship = self.current_ship_position[len(self.current_ship_position) - 1]

                #Statek jest pionowy
                if first_ship[0] == last_ship[0] and first_ship[1] != last_ship[1]:

                    lower_ship = self.current_ship_position[find_lowest_ship(self.current_ship_position)]
                    higher_ship = self.current_ship_position[find_highest_ship(self.current_ship_position)]

                    #Pierwszy ship jest nizej od drugiego
                    if lower_ship[1] - self.player_h == -1 and lower_ship[0] == self.player_w:
                        can_place = True
                    elif higher_ship[1] - self.player_h == 1 and higher_ship[0] == self.player_w:
                        can_place = True

                #Statek jest poziomy
                elif first_ship[0] != last_ship[0] and first_ship[1] == last_ship[1]:

                    left_ship = self.current_ship_position[find_left_ship(self.current_ship_position)]
                    right_ship = self.current_ship_position[find_right_ship(self.current_ship_position)]

                    #Pierwszy ship jest po prawej
                    if right_ship[0] - self.player_w == -1 and right_ship[1] == self.player_h:
                        can_place = True
                    elif left_ship[0] - self.player_w == 1 and left_ship[1] == self.player_h:
                        can_place = True


        return can_place
