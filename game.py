import socket
import pygame

WIDTH = 750
HEIGHT = 390

def Diff(li1, li2):
    li_dif = [i for i in li1 + li2 if i not in li1 or i not in li2]
    return li_dif

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

done = False

########### Images

crossImg = pygame.image.load('img/cross.png')
shipImg = pygame.image.load('img/ship_self.png')
missedShot = pygame.image.load('img/shotMissed.png')
shipKilled = pygame.image.load('img/shipKilled.png')

########### GAME

class Game():

    #active player
    #0 - player 1
    #1 - player 2

    # Stages:
    # 1. Picking place for our ships
    # 2. Waiting for both players to place ships
    # 3. Attacking enemy


    def __init__(self, player1, player2):
        self.players = [player1, player2]
        self.active_player = 0

    def start_conf(self):
        self.players[self.active_player].is_active = 1

    def draw_boards(self):
        self.players[self.active_player].draw_all()

    def place_ship_phase(self):
        self.players[0].is_active = 1
        self.players[1].is_active = 1

    def attack_enemy_phase(self):
        self.players[0].is_active = 1
        self.players[1].is_active = 0

    def place_attack(self, player_num):
        return self.players[player_num].place_attack()

    def change_turns(self):
        self.players[self.active_player].is_active = 0
        self.active_player = not self.active_player
        self.players[self.active_player].is_active = 1

    def checking_phase(self):
        if self.players[0].board.game_phase == 2 and self.players[1].board.game_phase == 2:
            self.players[0].board.game_phase = 3
            self.players[1].board.game_phase = 3
            return 2

        elif self.players[0].board.game_phase == 3 and self.players[1].board.game_phase == 3:
            return 3

        elif self.players[0].board.game_phase == 4 or self.players[1].board.game_phase == 4:
            return 4

        return 1

    def end_game(self):
        player1_game_phase = self.players[0].board.game_phase
        player2_game_phase = self.players[1].board.game_phase

        player_won_num = 0

        if player1_game_phase == 3:
            player_won_num = 0
        elif player1_game_phase == 4:
            player_won_num = 1

        player1_game_phase = 4
        player2_game_phase = 4

        for player in self.players:
            player.end_game(player_won_num)

    def game_loop(self):
        screen.fill((0,0,0))

        if self.checking_phase() == 1:
            self.place_ship_phase()
        elif self.checking_phase() == 3:
            self.attack_enemy_phase()
        elif self.checking_phase() == 4:
            self.end_game()

        self.draw_boards()

    def send_info_to_attacked_player(self, picked_square_in_width, picked_square_in_height):
        attacked_player_id = not self.active_player
        info = self.players[attacked_player_id].update_map_from_being_attacked(picked_square_in_width, picked_square_in_height)
        self.players[self.active_player].update_map_from_attack(info)

    def make_action(self):
        if self.checking_phase() == 1:
            self.players[self.active_player].place_ship()
        elif self.checking_phase() == 3:
            attack_cords = self.place_attack(self.active_player)
            if attack_cords != [-1, -1]:
                self.send_info_to_attacked_player(attack_cords[0], attack_cords[1])
                self.change_turns()
        elif self.checking_phase() == 4:
            self.end_game()


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
        self.is_active = 0

    def change_picked_square(self, width, height):
        if self.picked_square_in_width + width >= 0 and self.picked_square_in_width + width < self.board.dimension:
            self.picked_square_in_width = self.picked_square_in_width + width
        if self.picked_square_in_height + height >= 0 and self.picked_square_in_height + height < self.board.dimension:
            self.picked_square_in_height = self.picked_square_in_height + height
        self.draw_all()

    def draw_cross(self):
        self.board.draw_action(crossImg ,self.picked_square_in_width, self.picked_square_in_height)

    def draw_ship(self):
        self.board.draw_action(shipImg, self.picked_square_in_width, self.picked_square_in_height)

    def place_ship(self):
        self.board.place_ship(self.picked_square_in_width, self.picked_square_in_height)

    def place_attack(self):
        return self.board.place_attack(self.picked_square_in_width, self.picked_square_in_height)

    def draw_all(self):
        self.board.draw_all(self.picked_square_in_width, self.picked_square_in_height)

    def update_map_from_being_attacked(self, picked_square_in_width, picked_square_in_height):
        return self.board.update_map_from_being_attacked(picked_square_in_width, picked_square_in_height)

    def update_map_from_attack(self, info):
        self.board.update_map_from_attack(info)

    def end_game(self, player_won_num):
        self.board.end_game(player_won_num)


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
        self.padding_top = 60

        # Ships info

        self.ships_position = []
        self.current_ship_position = []
        self.shots_hit_position = []
        self.shots_missed_position = []
        self.placed_ships = 0
        self.placed_ships_figure = 0
        self.is_ship_being_placed = False
        self.ship_sizes = [ 1, 1]
        self.enemy_shoots_missed = []
        self.enemy_shoots_hit = []


        # Moves info

        self.game_phase = 1
        self.player_won_num = 0

    def end_game(self, player_won_num):
        self.player_won_num = player_won_num
        self.game_phase = 4
        self.draw_end_screen()


    def draw_board(self):
        for square_num_width in range(self.dimension):
            for square_num_height in range(self.dimension):

                square_x_pos = 50 + ( (WIDTH / 2) * self.player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
                square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

                pygame.draw.rect(screen, (255, 255, 255), (square_x_pos, square_y_pos, self.square_width, self.square_height))

    def draw_enemy_board(self):
        for square_num_width in range(self.dimension):
            for square_num_height in range(self.dimension):

                enemy_player_num = not self.player_num

                square_x_pos = 50 + ( (WIDTH / 2) * enemy_player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
                square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

                pygame.draw.rect(screen, (255, 255, 255), (square_x_pos, square_y_pos, self.square_width, self.square_height))

    def draw_enemy_boarder(self, sq_width_num, sq_height_num, valid):
        color = (255, 0, 0) #Red

        if valid is True:
            color = (0, 255, 0) #Green

        square_num_width = sq_width_num
        square_num_height = sq_height_num

        enemy_player_num = not self.player_num

        square_x_pos = 50 + ( (WIDTH / 2) * enemy_player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width)) - self.border_size
        square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height)) - self.border_size

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        pygame.draw.rect(screen, color, (square_x_pos, square_y_pos, square_width, square_height))

    def draw_ships(self):
        for ship in self.ships_position:
            for square_num_width in range(self.dimension):
                for square_num_height in range(self.dimension):
                    if ship[0] == square_num_width and ship[1] == square_num_height:
                        self.draw_action(shipImg, square_num_width, square_num_height)

    def draw_killed_ships(self):
        for ship in self.enemy_shoots_hit:
            for square_num_width in range(self.dimension):
                for square_num_height in range(self.dimension):
                    if ship[0] == square_num_width and ship[1] == square_num_height:
                        self.draw_action(shipKilled, square_num_width, square_num_height)

    def draw_missed_enemy_hits(self):
        for ship in self.enemy_shoots_missed:
            for square_num_width in range(self.dimension):
                for square_num_height in range(self.dimension):
                    if ship[0] == square_num_width and ship[1] == square_num_height:
                        self.draw_action(missedShot, square_num_width, square_num_height)

    def draw_missied_self_hits(self):
        for ship in self.shots_missed_position:
            for square_num_width in range(self.dimension):
                for square_num_height in range(self.dimension):
                    if ship[0] == square_num_width and ship[1] == square_num_height:
                        self.draw_action_on_enemy_board(missedShot, square_num_width, square_num_height)

    def draw_successfull_hits(self):
        for ship in self.shots_hit_position:
            for square_num_width in range(self.dimension):
                for square_num_height in range(self.dimension):
                    if ship[0] == square_num_width and ship[1] == square_num_height:
                        self.draw_action_on_enemy_board(shipKilled, square_num_width, square_num_height)

    def draw_border(self, sq_width_num, sq_height_num, valid):

        color = (255, 0, 0) #Red

        if valid is True:
            color = (0, 255, 0) #Green

        square_num_width = sq_width_num
        square_num_height = sq_height_num

        square_x_pos = 50 + ( (WIDTH / 2) * self.player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width)) - self.border_size
        square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height)) - self.border_size

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        pygame.draw.rect(screen, color, (square_x_pos, square_y_pos, square_width, square_height))

    def draw_action_attack(self, img, sq_width_num, sq_height_num):

        enemy_player_num = not self.player_num

        square_num_width = sq_width_num
        square_num_height = sq_height_num

        square_x_pos = 50 + ( (WIDTH / 2) * enemy_player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
        square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        screen.blit(img, (square_x_pos,square_y_pos))


    def draw_action(self, img, sq_width_num, sq_height_num):

        square_num_width = sq_width_num
        square_num_height = sq_height_num

        square_x_pos = 50 + ( (WIDTH / 2) * self.player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
        square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        screen.blit(img, (square_x_pos,square_y_pos))

    def draw_action_on_enemy_board(self, img, sq_width_num, sq_height_num):

        enemy_player_num = not self.player_num

        square_num_width = sq_width_num
        square_num_height = sq_height_num

        square_x_pos = 50 + ( (WIDTH / 2) * enemy_player_num ) + (22 * (square_num_width)) + (self.spacing_between * (square_num_width))
        square_y_pos = self.padding_top + (22 * (square_num_height)) + (self.spacing_between * (square_num_height))

        square_width = self.square_width + (2 * self.border_size)
        square_height = self.square_height + (2 * self.border_size)

        screen.blit(img, (square_x_pos,square_y_pos))

    def draw_main_text(self, text):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(text, True, (255,255,255), (0,0,0))
        textRect = text.get_rect()
        textRect.center = (WIDTH / 2, self.padding_top / 2)
        screen.blit(text, textRect)

    def draw_player_info_text(self, text):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text = font.render(text, True, (255,255,255), (0,0,0))
        textRect = text.get_rect()
        if self.player_num == 0:
            textRect.center = (WIDTH / 4, HEIGHT - 30)
        elif self.player_num == 1:
            textRect.center = (3 * WIDTH / 4, HEIGHT - 30)
        screen.blit(text, textRect)

    def draw_all_players_info_text(self, text_player1, text_player2):
        font = pygame.font.Font('freesansbold.ttf', 32)
        text1 = font.render(text_player1, True, (255,255,255), (0,0,0))
        text2 = font.render(text_player2, True, (255,255,255), (0,0,0))
        textRect1 = text1.get_rect()
        textRect2 = text2.get_rect()

        textRect1.center = (WIDTH / 4, HEIGHT - 30)
        textRect2.center = (3 * WIDTH / 4, HEIGHT - 30)

        screen.blit(text1, textRect1)
        screen.blit(text2, textRect2)

    def draw_end_screen(self):
        self.draw_board()
        self.draw_ships()
        self.draw_killed_ships()
        self.draw_missed_enemy_hits()
        self.draw_main_text("KONIEC GRY")
        if self.player_won_num == 0:
            self.draw_all_players_info_text("WYGRANY", "PRZEGRANY")
        elif self.player_won_num == 1:
            self.draw_all_players_info_text("PRZEGRANY", "WYGRANY")

    def draw_all(self, picked_square_in_width, picked_square_in_height):
        if self.game_phase == 1:
            self.draw_border(picked_square_in_width, picked_square_in_height, self.check_if_move_is_valid(picked_square_in_width, picked_square_in_height))
            self.draw_board()
            self.draw_ships()
            self.draw_action(shipImg, picked_square_in_width, picked_square_in_height)
            self.draw_main_text("UŁÓŻ STATKI")
            self.draw_player_info_text(str(self.ship_sizes[self.placed_ships_figure]) + " STATKA")

        elif self.game_phase == 2:
            self.draw_border(picked_square_in_width, picked_square_in_height, self.check_if_move_is_valid(picked_square_in_width, picked_square_in_height))
            self.draw_board()
            self.draw_ships()
            self.draw_action(crossImg, picked_square_in_width, picked_square_in_height)
            self.draw_main_text("ZACZEKAJ NA DRUGIEGO GRACZA")

        elif self.game_phase == 3:
            self.draw_enemy_boarder(picked_square_in_width, picked_square_in_height, self.check_if_attack_is_valid(picked_square_in_width, picked_square_in_height))
            self.draw_board()
            self.draw_enemy_board()
            self.draw_missied_self_hits()
            self.draw_successfull_hits()
            self.draw_ships()
            self.draw_killed_ships()
            self.draw_missed_enemy_hits()
            self.draw_action_attack(crossImg, picked_square_in_width, picked_square_in_height)
            self.draw_main_text("ATAK")

        elif self.game_phase == 4:
            self.draw_end_screen()

    def place_attack(self, picked_square_in_width, picked_square_in_height):
        if self.check_if_attack_is_valid(picked_square_in_width, picked_square_in_height):
            return [picked_square_in_width, picked_square_in_height]
        else:
            return [-1, -1]

    def place_ship(self, picked_square_in_width, picked_square_in_height):
        if self.check_if_move_is_valid(picked_square_in_width, picked_square_in_height):
            self.ships_position.append([picked_square_in_width, picked_square_in_height])
            self.current_ship_position.append([picked_square_in_width, picked_square_in_height])
            self.is_ship_being_placed = True
            self.placed_ships += 1

            if self.placed_ships == self.ship_sizes[self.placed_ships_figure]:
                self.is_ship_being_placed = False
                self.placed_ships = 0
                self.placed_ships_figure += 1
                self.current_ship_position = []

                #Jak ustawiliśmy już wszystkie statki to zmieniamy faze gry
                if self.placed_ships_figure == len(self.ship_sizes):
                    self.game_phase = 2

    def update_map_from_being_attacked(self, picked_square_in_width, picked_square_in_height):
        ship_hit = 0
        if [picked_square_in_width, picked_square_in_height] in self.ships_position:
            self.enemy_shoots_hit.append([picked_square_in_width, picked_square_in_height])
            ship_hit = 1
        else:
            self.enemy_shoots_missed.append([picked_square_in_width, picked_square_in_height])

        if len(Diff(self.enemy_shoots_hit, self.ships_position)) == 0:
            self.game_phase = 4

        return [picked_square_in_width, picked_square_in_height, ship_hit]

    def update_map_from_attack(self, info):
        #Hit
        if info[2] == 1:
            self.shots_hit_position.append([info[0], info[1]])
        #Miss
        elif info[2] == 0:
            self.shots_missed_position.append([info[0], info[1]])


    def check_if_attack_is_valid(self, picked_square_in_width, picked_square_in_height):
        if [picked_square_in_width, picked_square_in_height] in self.shots_missed_position or [picked_square_in_width, picked_square_in_height] in self.shots_hit_position:
            return False
        return True

    def check_if_move_is_valid(self, picked_square_in_width, picked_square_in_height):
        if self.game_phase == 1:

            #Jak jeszcze nie postawiliśmy
            if self.is_ship_being_placed == False:
                can_place = True
                for ship in self.ships_position:
                    if ship[0] == picked_square_in_width - 1 and ship[1] == picked_square_in_height - 1:
                        can_place = False
                    elif ship[0] == picked_square_in_width and ship[1] == picked_square_in_height - 1:
                        can_place = False
                    elif ship[0] == picked_square_in_width + 1 and ship[1] == picked_square_in_height - 1:
                        can_place = False
                    elif ship[0] == picked_square_in_width - 1 and ship[1] == picked_square_in_height:
                        can_place = False
                    elif ship[0] == picked_square_in_width and ship[1] == picked_square_in_height:
                        can_place = False
                    elif ship[0] == picked_square_in_width + 1 and ship[1] == picked_square_in_height:
                        can_place = False
                    elif ship[0] == picked_square_in_width - 1 and ship[1] == picked_square_in_height + 1:
                        can_place = False
                    elif ship[0] == picked_square_in_width and ship[1] == picked_square_in_height + 1:
                        can_place = False
                    elif ship[0] == picked_square_in_width + 1  and ship[1] == picked_square_in_height + 1:
                        can_place = False

            #Jak już postawiliśmy jakiś statek
            elif self.is_ship_being_placed == True:
                can_place = False



                if self.placed_ships == 1:

                    can_place = True

                    for ship in self.current_ship_position:
                        if ship[0] == picked_square_in_width and ship[1] == picked_square_in_height:
                            can_place = False
                        elif ship[0] == picked_square_in_width - 1 and ship[1] == picked_square_in_height - 1:
                            can_place = False
                        elif ship[0] == picked_square_in_width + 1 and ship[1] == picked_square_in_height + 1:
                            can_place = False
                        elif ship[0] == picked_square_in_width - 1 and ship[1] == picked_square_in_height + 1:
                            can_place = False
                        elif ship[0] == picked_square_in_width + 1 and ship[1] == picked_square_in_height - 1:
                            can_place = False
                        elif abs(ship[0] - picked_square_in_width) > 1 or abs(ship[1] - picked_square_in_height) > 1:
                            can_place = False

                elif self.placed_ships > 1:

                    first_ship = self.current_ship_position[0]
                    last_ship = self.current_ship_position[len(self.current_ship_position) - 1]

                    #Statek jest pionowy
                    if first_ship[0] == last_ship[0] and first_ship[1] != last_ship[1]:

                        lower_ship = self.current_ship_position[self.find_lowest_ship()]
                        higher_ship = self.current_ship_position[self.find_highest_ship()]

                        #Pierwszy ship jest nizej od drugiego
                        if lower_ship[1] - picked_square_in_height == -1 and lower_ship[0] == picked_square_in_width:
                            can_place = True
                        elif higher_ship[1] - picked_square_in_height == 1 and higher_ship[0] == picked_square_in_width:
                            can_place = True

                    #Statek jest poziomy
                    elif first_ship[0] != last_ship[0] and first_ship[1] == last_ship[1]:

                        left_ship = self.current_ship_position[self.find_left_ship()]
                        right_ship = self.current_ship_position[self.find_right_ship()]

                        #Pierwszy ship jest po prawej
                        if right_ship[0] - picked_square_in_width == -1 and right_ship[1] == picked_square_in_height:
                            can_place = True
                        elif left_ship[0] - picked_square_in_width == 1 and left_ship[1] == picked_square_in_height:
                            can_place = True


            return can_place



    def find_lowest_ship(self):
        max = 0
        id = 0
        for index, ship in enumerate(self.current_ship_position):
            if ship[1] > max:
                max = ship[1]
                id = index
        return id

    def find_highest_ship(self):
        min = 10
        id = 0
        for index, ship in enumerate(self.current_ship_position):
            if ship[1] < min:
                min = ship[1]
                id = index
        return id

    def find_right_ship(self):
        max = 0
        id = 0
        for index, ship in enumerate(self.current_ship_position):
            if ship[0] > max:
                max = ship[0]
                id = index
        return id

    def find_left_ship(self):
        min = 10
        id = 0
        for index, ship in enumerate(self.current_ship_position):
            if ship[0] < min:
                min = ship[0]
                id = index
        return id

player1 = Player(0)
player2 = Player(1)

game = Game(player1, player2)
game.start_conf()


while not done:

    active_player = game.players[game.active_player]
    game.game_loop()

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
                        game.make_action()
                    elif event.key == pygame.K_SPACE:
                        game.change_turns()

    pygame.display.flip()
