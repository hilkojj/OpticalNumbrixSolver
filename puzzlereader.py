import pytesseract
from PIL import Image

CROP_MARGIN = 12


def puzzle_from_img(puzzle_img_path, puzzle_size):
    puzzle = [[0 for j in range(puzzle_size)] for i in range(puzzle_size)]  # 2d array of zeros

    img = Image.open(puzzle_img_path)

    img_res = img.size[0]
    piece_size = img_res / puzzle_size

    i = 0
    for x in range(puzzle_size):
        for y in range(puzzle_size):
            cropped = img.crop(
                (x * piece_size + CROP_MARGIN,
                 y * piece_size + CROP_MARGIN,
                 x * piece_size + piece_size - CROP_MARGIN,
                 y * piece_size + piece_size - CROP_MARGIN)
            )

            value = (pytesseract.image_to_string(cropped, config='--psm 10')
                     .replace("l", "1")  # a L might look like an 1
                     .replace("@", "1")  # a 1 in an circle is read as a @
                     )

            i += 1
            print("\rReading puzzle {}%".format(str(i / puzzle_size ** 2 * 100).split(".")[0]), end="")

            if not value.isdigit():
                continue

            puzzle[y][x] = int(value)

    print("\nReading puzzle done")
    return puzzle
