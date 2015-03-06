import os, pygame
import textwrap
from pygame.locals import SRCALPHA

class Resources(object):
    def __init__(self):
        pygame.font.init()
        try:
            main_dir = os.path.split(os.path.abspath(__file__))[0]
        except NameError:
            main_dir = os.path.split(os.path.abspath(sys.argv[0]))[0]
        if main_dir[len(main_dir)-4:]=='.exe': #Hack for compiling
            main_dir = os.path.join(main_dir, '..')
        self.dir = os.path.join(main_dir, 'resources')
    def load_image(self, name):
        fullname = os.path.join(self.dir, name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error, message:
            print 'Cannot load image:', name
            raise SystemExit, message
        return image
    def unpack_sheet(self, name):
        results = []
        sheet = self.load_image(name+'.png')
        with open(os.path.join(self.dir, name+'.txt'), 'r') as sheet_map:
            for i, line in enumerate(sheet_map):
                if i==0:
                    ignore = len(line.split()[0])-1
                index=(int(line.split()[0][ignore::]))
                x_start=(int(line.split()[2]))
                y_start=(int(line.split()[3]))
                x_size=(int(line.split()[4]))
                y_size=(int(line.split()[5]))
                cutout = (x_start, y_start, x_size, y_size)
                while len(results)<index+1:
                    results.append(pygame.Surface((x_size, y_size), flags=SRCALPHA))
                results[index].blit(sheet, (0, 0), cutout)
        return results
    def load_font(self, size):
        fontpath = os.path.join(self.dir, "Code New Roman b.otf")
        return pygame.font.Font(fontpath, size)
    def play_music(self, name):
        """Generic function to play music in PyGame"""
        class NoneSound:
            def play(self): pass
        if not pygame.mixer or not pygame.mixer.get_init():
            return NoneSound()
        fullname = os.path.join(self.dir, name)
        try:
            pygame.mixer.music.load(fullname)
        except pygame.error:
            print ('Cannot load music: %s' % fullname)
            raise SystemExit(str(geterror()))
        pygame.mixer.music.set_volume(0.3)
        pygame.mixer.music.play(-1)
    def load_sound(self, name):
        """Generic function to load sounds in PyGame"""
        class NoneSound:
            def play(self): pass
        if not pygame.mixer or not pygame.mixer.get_init():
            return NoneSound()
        fullname = os.path.join(self.dir, name)
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error:
            print ('Cannot load sound: %s' % fullname)
            raise SystemExit(str(geterror()))
        sound.set_volume(0.2)
        return sound
    def string2image(self, text, wraplength=200, fontsize=14,
                    textcolor=(255, 255, 255), bgcolor=(0, 0, 0), 
                    border=0):
        '''Takes a list of strings and returns an image.'''
        wraplength = int((wraplength)*1.7/fontsize)
        wrapped_text = []
        for line in text:
            wrapped_text+=textwrap.wrap(line, wraplength)
        line_images = []
        fontpath = os.path.join(self.dir, "Code New Roman.otf")
        font = pygame.font.Font(fontpath, fontsize)
        max_length = 0
        for line in wrapped_text:
            line_images.append(font.render(line, 1, textcolor, bgcolor))
            if len(line)>max_length:
                max_length = len(line)
        box_height = int(len(wrapped_text)*fontsize + border*2)
        box_width = int(max_length/1.7*fontsize + border*2)
        image = pygame.Surface((box_width, box_height))
        image.fill(bgcolor)
        for i, line in enumerate(wrapped_text):
            image.blit(line_images[i], (border, int(border+i*fontsize)))
        return image
res = Resources()