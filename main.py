import pygame
import title
import avatar

class Main(object):
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.ratio = (16, 12)
        self.canvas = pygame.Surface((self.ratio[0]*40, self.ratio[1]*40))
        self.clock = pygame.time.Clock()
        self.data = None
        self.routine = title.Title(self)
        self.mouse_stationary_time = 0
        self.quit = False
    def draw(self):
        if self.canvas.get_rect() != pygame.display.get_surface().get_rect():
            scaled_canvas = pygame.transform.smoothscale(self.canvas,
                (pygame.display.get_surface().get_width(),
                pygame.display.get_surface().get_height()))
            self.screen.blit(scaled_canvas, (0,0))
        else:
            self.screen.blit(self.canvas, (0,0))
        pygame.display.flip()
    def event_handler(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True
            elif event.type == pygame.VIDEORESIZE:
                self.screen=pygame.display.set_mode(event.dict['size'], pygame.RESIZABLE)
            elif event.type in [pygame.MOUSEMOTION, pygame.MOUSEBUTTONUP,
                                pygame.MOUSEBUTTONDOWN]:
                self.mouse_stationary_time = 0
                pos = event.pos
                pos = (pos[0]*640/pygame.display.get_surface().get_width(),
                        pos[1]*480/pygame.display.get_surface().get_height())
                for sprite in self.routine.ui.sprites():
                    if sprite.rect.collidepoint(pos):
                        sprite.input(self.routine, event)
                    elif sprite.active:
                        sprite.active = False
                        sprite.held = False
                        sprite.lose_focus()
    def run(self):
        while True:
            if self.quit == True:
                return
            self.event_handler()
            self.routine.run()
            self.draw()
            self.mouse_stationary_time += 1
            if self.mouse_stationary_time == 30:
                for sprite in self.routine.ui.sprites():
                    if sprite.active:
                        sprite.mousestay(self.routine)
            self.clock.tick(30)