from pathlib import Path
import os, csv
from random import randint, shuffle

class Crossword():
    # Coordinate indexes
    ROW = 0
    COL = 1

    EMPTY_SQUARE = " "

    MAP_WIDTH = 20
    MAP_LENGTH = 20
    
    def __init__(self):
        self.folder_path = Path(os.path.dirname(os.path.abspath(__file__)))
        self.output_file_path = self.folder_path / "crossword.csv"

        self.crossword_map = []
        self.map_coordinates = []
        self.letter_positions = {}
        # Words in a crossword only goes down and right
        self.word_vectors = [(0,1),(1,0)]
        self.word_vector = ()
        self.start_coord = ()
        self.unplaced_words = []

    def initialize_crossword_map(self):
        self.crossword_map = [[self.EMPTY_SQUARE]*self.MAP_WIDTH for _ in range(self.MAP_LENGTH)]

    def initialize_map_coordinates(self):
        self.map_coordinates = []
        for i in range(self.MAP_LENGTH):
            for j in range(self.MAP_WIDTH):
                self.map_coordinates.append((i,j))

    def generate(self, words:list):
        self.initialize_crossword_map()
        self.initialize_map_coordinates()
        self.insert_words_into_map(words)

    def insert_words_into_map(self, words:list):
        # Place first word
        first_word_idx = self.place_first_word_into_map(words)
        if first_word_idx is None:
            return
        words.pop(first_word_idx)
        # Place remaining words
        while(words):
            prev_words_count = len(words)
            for word_idx, word in enumerate(words):
                is_word_inserted = False
                for letter_idx, letter in enumerate(word):
                    # Checks if the letter is on the board
                    if letter not in self.letter_positions.keys():
                        continue
                    letter_positions = self.letter_positions[letter]
                    shuffle(letter_positions)
                    for position in letter_positions:
                        if self.can_insert_into_map(word, position, letter_idx=letter_idx):
                            self.place_word_into_map(word, self.start_coord)
                            words.pop(word_idx)
                            is_word_inserted = True
                            break
                    if is_word_inserted:
                        break
            # If no new words were placed on the board
            if len(words) == prev_words_count:
                self.unplaced_words = words
                break

    def place_first_word_into_map(self, words:list) -> int:
        """Places the first word onto the map. If the word is placed, the index of the word placed in words is return.
        If not, None is returned."""
        first_word_idx = randint(0,len(words)-1)
        first_word = words[first_word_idx]
        # Place in the center
        coord = (self.MAP_LENGTH//2,self.MAP_WIDTH//2)
        if self.can_insert_into_map(first_word, coord,True):
            self.place_word_into_map(first_word, coord)
            return first_word_idx
        # Place in a random position if the word could not be placed in the center position
        shuffle(self.map_coordinates)
        for coord in self.map_coordinates:
            if self.can_insert_into_map(first_word, coord,True):
                self.place_word_into_map(first_word, coord)
                return first_word_idx
        return None
            
    def can_insert_into_map(self, word:str, letter_coord:tuple, is_first_word:bool=False, letter_idx:int=0) -> bool:
        shuffle(self.word_vectors)
        for vector in self.word_vectors:
            if not is_first_word:
                start_row = letter_coord[self.ROW]-vector[self.ROW]*letter_idx
                start_col = letter_coord[self.COL]-vector[self.COL]*letter_idx
                coords = (start_row,start_col)
            else:
                coords = letter_coord
            if not self.is_within_map(coords):
                continue
            if not self.can_fit_in_map(word, coords,vector):
                continue
            # The first word can be placed anywhere on the map
            if is_first_word:
                self.word_vector = vector
                return True
            if not self.is_valid_path(word, coords, vector, letter_coord):
                continue
            self.start_coord = coords
            self.word_vector = vector
            return True
        return False
    
    def is_valid_path(self, word:str, start_coord:tuple, vector:tuple, letter_coord:tuple) -> bool:
        for i in range(len(word)):
            row = vector[self.ROW]*i+start_coord[self.ROW]
            col = vector[self.COL]*i+start_coord[self.COL]
            if (row,col) == letter_coord:
                if not self.is_parallel_squares_empty((row,col), vector):
                    return False
                continue
            if self.crossword_map[row][col] != self.EMPTY_SQUARE:
                return False
            if not self.is_surrounding_squares_empty((row,col), letter_coord):
                return False
        return True
    
    def is_surrounding_squares_empty(self, coord:tuple, letter_coord:bool=False) -> bool:
        vectors = [(0,1),(0,-1),(1,0),(-1,0)]
        for vector in vectors:
            row = coord[self.ROW]+vector[self.ROW]
            col = coord[self.COL]+vector[self.COL]
            if (row,col) == letter_coord:
                continue
            if not self.is_within_map((row,col)):
                continue
            if self.crossword_map[row][col] != self.EMPTY_SQUARE:
                return False
        return True

    def is_parallel_squares_empty(self, coord, vector) -> bool:
        opposite_vector = tuple(-1*i for i in vector)
        vectors = (vector, opposite_vector)
        for vector in vectors:
            row = coord[self.ROW]+vector[self.ROW]
            col = coord[self.COL]+vector[self.COL]
            if self.crossword_map[row][col] != self.EMPTY_SQUARE:
                return False
        return True

    def can_fit_in_map(self, word:str, starting_coord:tuple, vector:tuple) -> bool:
        word_length = len(word)
        word_end_position = self.return_end_position(word_length, starting_coord, vector)
        if not self.is_within_map(word_end_position):
            return False
        return True
    
    def return_end_position(self, word_length:int, start_coord:tuple, vector:tuple) -> tuple:
        return (vector[self.ROW]*word_length+start_coord[self.ROW], vector[self.COL]*word_length+start_coord[self.COL])

    def is_within_map(self, pos:tuple) -> bool:
        return (pos[self.ROW] < self.MAP_LENGTH and
                pos[self.ROW] >= 0 and
                pos[self.COL] < self.MAP_WIDTH and
                pos[self.COL] >= 0)

    def place_word_into_map(self, word:str, start_coord:tuple):
        for i, letter in enumerate(word):
            row = i*self.word_vector[self.ROW]+start_coord[self.ROW]
            col = i*self.word_vector[self.COL]+start_coord[self.COL]
            self.crossword_map[row][col] = letter
            if letter not in self.letter_positions.keys():
                self.letter_positions[letter] = [(row,col)]
            else:
                self.letter_positions[letter].append((row,col))

    def output_to_file(self):
        with open(self.output_file_path, mode="w", newline="") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerows(self.crossword_map)

if __name__ == "__main__":
    word_list = ["cookie","milk","cake", "present","tree","toy", "stocking", "reindeer", "santa", "elf"]
    crossword = Crossword()
    crossword.generate(word_list)
    crossword.output_to_file()