def find_lowest_ship(array):
    max = 0
    id = 0
    for index, ship in enumerate(array):
        if ship[1] > max:
            max = ship[1]
            id = index
    return id

def find_highest_ship(array):
    min = 10
    id = 0
    for index, ship in enumerate(array):
        if ship[1] < min:
            min = ship[1]
            id = index
    return id

def find_right_ship(array):
    max = 0
    id = 0
    for index, ship in enumerate(array):
        if ship[0] > max:
            max = ship[0]
            id = index
    return id

def find_left_ship(array):
    min = 10
    id = 0
    for index, ship in enumerate(array):
        if ship[0] < min:
            min = ship[0]
            id = index
    return id

def check_if_arrays_are_equal(array1, array2):
    longer_array = array1 if len(array1) > len(array2) else array2

    same = True
    for coords in longer_array:
        if coords not in array2:
            same = False

    return same
