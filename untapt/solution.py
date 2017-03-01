class Rover():
    def __init__(self, x, y, facing):
        if all(coord >= 0 for coord in [x, y]):
            self.x = int(x)
            self.y = int(y)
        else:
            raise ValueError('Cannot initiate a rover with negative coordinates')
        self.facing = facing.upper()
        self.left = {'N': 'W', 'W': 'S', 'S': 'E', 'E': 'N'}
        self.right = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}
        self.move = {'N': [0, 1], 'E': [1, 0], 'S': [0, -1], 'W': [-1, 0]}

    def get_position(self):
        "Return the position of the rover as a dictionary"
        return {'x': self.x, 'y': self.y, 'facing': self.facing}

    def get_next_position_if_moved(self):
        """
        Returns the coordinates that the rover would move to if it did move.
        Use this to make sure rovers aren't running off of the plateau
        """
        movement = self.move[self.facing]
        x = self.x + movement[0]
        y = self.y + movement[1]
        return [x, y]

    def move_forward(self):
        """
        Moves the rover forward one space, relative to its facing.
        Doesn't move the rover if it would land it in a negative
        coordinate.
        """
        new_position = self.get_next_position_if_moved()
        # Make sure the rover isn't moving off the left or bottom edges
        if all(coord >= 0 for coord in new_position):
            self.x, self.y = new_position
        else:
            print 'Movement failed, cannot move to negative coordinates'

    def turn_left(self):
        "Turns the rover 90 degrees to the left"
        self.facing = self.left[self.facing]

    def turn_right(self):
        "Turns the rover 90 degrees to the right"
        self.facing = self.right[self.facing]


class Plateau():
    def __init__(self, x, y):
        if all(coord >= 0 for coord in [x, y]):
            self.far_right = int(x)
            self.top = int(y)
            self.retired_rovers = []
            self.rover = False
        else:
            raise ValueError('Cannot initiate a plateau with negative coordinates')

    def create_rover(self, x, y, facing):
        """
        Retires the current active rover if there is one, and
        creates a new active rover.
        """
        x, y = int(x), int(y)
        facing = facing.upper()
        if self.rover:
            self.retired_rovers.append(self.rover)
        self.rover = Rover(x, y, facing)

    def rover_check(self):
        "Makes sure the current rover exists"
        assert self.rover, 'You cannot perform an operation on a rover without creating one first'

    def move_rover(self):
        """
        Moves the current rover if there is one, unless it would move it off of the top
        or right edges of the plateau. Doesn't move the rover if it would cause it to
        fall off of the plateau
        """
        self.rover_check()
        next_position = self.rover.get_next_position_if_moved()
        # Make sure the next position isn't off of the top or right edges of the plateau
        if next_position[0] > self.far_right or next_position[1] > self.top:
            print 'Movement failed, cannot move rover off the edge of the plateau'
            return
        self.rover.move_forward()

    def turn_rover_left(self):
        "Turns the current rover 90 degrees to the left"
        self.rover_check()
        self.rover.turn_left()

    def turn_rover_right(self):
        "Turns the current rover 90 degrees to the right"
        self.rover_check()
        self.rover.turn_right()

    def print_rovers(self):
        "Prints the position of each rover formatted to the expected output."
        if self.rover:
            self.retired_rovers.append(self.rover)
        for rover in self.retired_rovers:
            position = rover.get_position()
            print "{} {} {}".format(position['x'], position['y'], position['facing'])


def main():
    user_input = raw_input('Please input the upper-right coordinates of the plateau\n')
    plat_args = map(int, user_input.split()[:2])

    plat = Plateau(*plat_args)
    plat_commands = {'R': plat.turn_rover_right,
                     'L': plat.turn_rover_left,
                     'M': plat.move_rover}

    # Loop for the rest of the input
    user_input = raw_input()
    task_count = 0
    while user_input:
        if task_count % 2 == 0:  # Create and retire a rover
            rover_args = user_input.split()[:3]
            rover_args[:2] = map(int, rover_args[:2])
            plat.create_rover(*rover_args)
        else:  # Execute movements on the current active rover
            movements = list(user_input)
            for movement in movements:
                plat_commands[movement]()

        user_input = raw_input()
        task_count += 1

    # Print the result
    plat.print_rovers()


if __name__ == '__main__':
    debug = False  # Set to True to run tests, or False to run the program

    if debug:
        import unittest

        class RoverTest(unittest.TestCase):
            def setUp(self):
                self.rover = Rover(1, 1, 'N')

            def test_turn_rover_left(self):
                result = []
                expected = ['W', 'S', 'E', 'N']
                for x in range(4):
                    self.rover.turn_left()
                    result.append(self.rover.facing)
                self.assertEqual(result, expected)

            def test_turn_rover_right(self):
                result = []
                expected = ['E', 'S', 'W', 'N']
                for x in range(4):
                    self.rover.turn_right()
                    result.append(self.rover.facing)
                self.assertEqual(result, expected)

            def test_move_rover_north(self):
                x, y = self.rover.x, self.rover.y
                self.rover.move_forward()
                self.assertEqual(x, self.rover.x)
                self.assertEqual(y+1, self.rover.y)

            def test_move_rover_east(self):
                rover = Rover(1, 1, 'E')
                x, y = rover.x, rover.y
                rover.move_forward()
                self.assertEqual((x+1, y), (rover.x, rover.y))

            def test_move_rover_west(self):
                rover = Rover(1, 1, 'W')
                x, y = rover.x, rover.y
                rover.move_forward()
                self.assertEqual((x-1, y), (rover.x, rover.y))

            def test_move_rover_south(self):
                rover = Rover(1, 1, 'S')
                x, y = rover.x, rover.y
                rover.move_forward()
                self.assertEqual((x, y-1), (rover.x, rover.y))

            def test_fail_to_move_to_negative_coords(self):
                rover1 = Rover(0, 0, 'W')
                rover2 = Rover(0, 0, 'S')
                rover1.move_forward()
                rover2.move_forward()
                result = (rover1.x, rover1.y, rover2.x, rover2.y)
                self.assertTrue(all(res == 0 for res in result))

        class PlateauTest(unittest.TestCase):
            def test_instantiate_valid_plateau(self):
                plat1 = Plateau(5, 10)
                plat2 = Plateau(0, 0)
                plat3 = Plateau(2.5, 3.5)
                inputs = ((plat1.far_right, 5), (plat1.top, 10),
                          (plat2.far_right, 0), (plat2.top, 0),
                          (plat3.far_right, 2), (plat3.top, 3))
                self.assertTrue(all(t[0] == t[1] for t in inputs))

            def test_instantiate_invalid_plateau(self):
                inputs = ((-1, 0), (5, -1), (-6, -10))
                for i in inputs:
                    with self.assertRaises(ValueError) as context:
                        Plateau(i[0], i[1])

                    self.assertTrue('Cannot initiate a plateau with negative coordinates' in context.exception)

            def test_create_rover(self):
                plat = Plateau(5, 5)
                plat.create_rover(1, 2, 'N')
                rover = plat.rover
                plat.create_rover(3, 4, 'E')
                self.assertEqual(plat.retired_rovers, [rover])
                self.assertEqual(plat.rover.x, 3)
                self.assertEqual(plat.rover.y, 4)
                self.assertEqual(plat.rover.facing, 'E')

            def test_fail_to_move_rover_off_plateau(self):
                result = []
                plat = Plateau(5, 5)
                plat.create_rover(5, 5, 'N')
                # Fail to move off the top of the plateau
                plat.move_rover()
                result.append(plat.rover.x)
                result.append(plat.rover.y)

                plat.create_rover(5, 5, 'E')
                # Fail to move off the right side of the plateau
                plat.move_rover()
                result.append(plat.rover.x)
                result.append(plat.rover.y)
                self.assertTrue(all(res == 5 for res in result))

        unittest.main()

    else:
        # Run the program
        main()
