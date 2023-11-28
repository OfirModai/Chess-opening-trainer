import time
import pygame
import Data.mongo_service as mongo_service
from Game import Game


def play_game(color):
    run = True
    screen = pygame.Rect(0, 0, 1200, 700)
    pygame.init()
    game = Game(color, screen)
    game.draw()
    while run is True:
        time.sleep(0.1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            else:
                massage = game.get_event(event)
                if massage == 'main':
                    run = massage
                if massage is not False:
                    game.draw()

    if game.buttons['mode'].text == 'setting':
        mongo_service.update_book()
    pygame.quit()
    if run == 'main':
        main()


def main():
    mongo_service.get_client_connection()
    names = mongo_service.client['Chess_opening_trainer'].list_collection_names()
    names.insert(0, 'display guidelines')
    names.append('create new book')
    collections_line = ''
    for c, i in zip(names, range(0, 50)):
        collections_line += f'{i}. {c}, '
    collections_line = collections_line[:-2]
    n = 0
    while n == 0:
        print("Select book:")
        print(collections_line)
        n = input()
        # n = 2
        try:
            n = int(n)
            if n >= len(names) or n < 0: n / 0
        except:
            print('not a valid input')
            n = 0
            continue
        if n == 0:
            print('hey there! here are some guidelines for using this trainer: \n'
                  'clicking on the text below the board will let you type comments on a position, the headline '
                  'is changeable as well \nto go back to the choosing screen click main \n'
                  'the already known variations are on the right side, click on them will apply the move '
                  'you can change the mode with clicking on the settings', )
        elif len(names) == n - 1:
            mongo_service.load_book(input('enter the new book\'s name:'))
            mongo_service.active_book.insert_one(
                {'_id': '999', 'orientation': input('enter color to play in the book')})
        else:
            mongo_service.load_book(names[n])
    play_game(mongo_service.active_book.find({'_id': '999'})[0]['orientation'])


if __name__ == "__main__":
    main()
