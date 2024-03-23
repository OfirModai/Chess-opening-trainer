import math

import pygame

from Gameplay import GameOperations


class Button:
    def __init__(self, name, text, font, point, keep, editable=False, maximumwidth=math.inf, columns=1):
        self.name = name
        self.editable = editable
        self.point = point
        self.columns = columns
        self.font = font
        self.keep = keep
        self.clicked = False
        self.text: str = text
        self.maximumwidth = maximumwidth
        self.surfaces = []
        self.rects = []
        self.write(text)

    def write(self, text):
        self.text = text
        self.rects.clear()
        self.surfaces.clear()
        words = text.split(' ')
        if self.columns != 1:
            if len(words) > 0 and words[0] == "PGN:": words.pop(0)
            self.__write_chart(words, self.columns)
            return
        letters_per_line = math.floor(self.maximumwidth / self.font.size(' ')[0]) if self.maximumwidth is not math.inf \
            else math.inf
        while len(words) > 0:
            text = ''
            while len(words) > 0:
                # loop for building a line
                word = words.pop(0)
                if word == '\n': break
                elif self.font.size(text + word + ' ')[0] > self.maximumwidth:
                    if self.font.size(word)[0] > self.maximumwidth:
                        words.insert(0, word[int(len(word)/2):])
                        words.insert(0, word[:int(len(word)/2)])
                    else:
                        words.insert(0, word)
                    break
                text += word + ' '
            self.surfaces.append(self.font.render(text, True, (225, 225, 225), (127, 127, 127)))
            rect = self.surfaces[-1].get_rect()
            point = self.point
            if len(self.rects) > 0:
                point = (point[0], point[1] + self.rects[-1].height * len(self.rects))
            setattr(rect, self.keep, point)
            self.rects.append(rect)

    def __write_chart(self, words, columns):
        while len(words) > 0:
            for i in range(columns):
                if len(words) == 0: continue
                text = words.pop(0)
                self.surfaces.append(self.font.render(text, True, (225, 225, 225), (127, 127, 127)))
                rect = self.surfaces[-1].get_rect()
                y = self.rects[-columns].bottom + 20 if len(self.rects) >= columns else self.point[1]
                x = self.point[0] + i * int(self.maximumwidth/columns)
                setattr(rect, self.keep, (x, y))
                self.rects.append(rect)

    def get_text_clicked(self, pos):
        if self.columns == 1: return self.text
        for surface in self.rects:
            if surface.collidepoint(pos):
                return self.text.split(' ')[self.rects.index(surface)]
        return False

    def get_option(self, indx=None):
        """
        :param indx: position of the word, if not given, get random one
        :return:
        """
        words = self.text.split(" ")
        if indx is None: return words[GameOperations.get_random(len(words))]
        return words[indx]

    def add_to_text(self, text):
        self.write(self.text + text)

    def delete_one(self):
        self.write(self.text[0:-1])

    def __str__(self):
        return f'name: {self.name} text: {self.text}'
