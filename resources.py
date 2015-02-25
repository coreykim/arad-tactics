import os, pygame

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
                index=(int(line.split()[0]))
                x_start=(int(line.split()[2]))
                y_start=(int(line.split()[3]))
                x_size=(int(line.split()[4]))
                y_size=(int(line.split()[5]))
                results.append(pygame.Surface((x_size, y_size), flags=SRCALPHA))
            for i, line in enumerate(sheet_map):
                cutout = (x_start, y_start, x_size, y_size)
                results[index].blit(sheet, (0, 0), cutout)
        return results
    def load_font(self, size):
        fontpath = os.path.join(self.dir, "Code New Roman.otf")
        return pygame.font.Font(fontpath, size)
res = Resources()