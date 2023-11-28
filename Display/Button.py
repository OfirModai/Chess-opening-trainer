import math

import pygame


class Button:
    def __init__(self, name, text, font, point, keep, editable=False, maximumwidth=math.inf):
        self.name = name
        self.editable = editable
        self.point = point
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
        if words[0] == 'PNG:':
            self.__write_chart(words[1:-1], 3)
            return
        letters_per_line = math.floor(self.maximumwidth / self.font.size(' ')[0]) if self.maximumwidth is not math.inf \
            else math.inf
        while len(words) > 0:
            text = ''
            count = letters_per_line
            while len(words) > 0 and count > len(words[0]):
                word = words.pop(0)
                if word == '\n': break
                count -= (len(word) + 1)
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
                y = self.rects[-columns].bottom if len(self.rects) >= columns else self.point[1]
                x = self.point[0] + i * int(self.maximumwidth/columns)
                setattr(rect, self.keep, (x, y))
                self.rects.append(rect)

    def add_to_text(self, text):
        self.write(self.text + text)

    def delete_one(self):
        self.write(self.text[0:-1])

    def __str__(self):
        return f'name: {self.name} text: {self.text}'
