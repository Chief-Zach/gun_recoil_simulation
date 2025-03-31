from typing import Union, ClassVar
from sprites import *
import pygame
from scipy.integrate import ode
import sys

BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 0)
RED = (255, 0, 0, 255)
GREEN = (0, 255, 0, 255)
BLUE = (0, 0, 255, 255)

class Simulation:
    def __init__(self):
        self.paused = True # starting in paused mode
        self.title = title
        self.cur_time = 0
        self.dt = 0.033
        self.g = 9.8
        self.times = []
        self.positions = []
        self.gun_momentum = None
        self.state = None
        self.powder_weight = None
        self.gun_weight = None
        self.solver = None
        self.mv = None
        self.bullet_momentum = None
        self.gas_momentum = None
        self.je_momentum = None
        self.bullet_weight = None
        self.shoot = False
        self.gas_exit_velocity =  None
        self.gun_velocity = None
        self.resistance = None
        self.initial_x = None
        self.resisting_force = 0

    def init(self, state, powder_weight, gun_weight, bullet_weight, mv: Union[int, float] = 1000, resistance=0.3):
        self.state = state
        self.initial_x = state[0]
        self.powder_weight = powder_weight
        self.resistance = resistance
        self.gun_weight = gun_weight
        self.mv = mv
        self.bullet_weight = bullet_weight
        self.setup_gun()
        self.set_integrator()

    def set_integrator(self):
        self.solver = ode(self.f)
        self.solver.set_integrator('dopri5')

        self.solver.set_initial_value(self.state, self.cur_time)

    def fire(self):
        print("FIRING")
        self.shoot = True

    def f(self, t):
        x, y, vx, vy = self.state
        dxdt = vx
        dydt = vy

        # Resisting force based on current velocity
        resisting_force = self.resistance * self.gun_velocity if x > self.initial_x or self.shoot else 0
        # resisting_force = 1443.706426034108 if x > self.initial_x or self.shoot else 0
        # Compute acceleration based on forces
        dvxdt = -resisting_force  # Negative because it's opposing motion
        dvydt = 0

        if self.shoot:

            dvxdt += self.gun_velocity
            print(f"Applied gun velocity {self.gun_velocity} and resisting force {resisting_force}")

        return [dxdt, dydt, dvxdt, dvydt]
    def pause(self):
        self.paused = True

    def resume(self):
        self.paused = False

    def step(self):
        if self.paused or not self.solver.successful():
            return

        self.solver.integrate(self.cur_time + self.dt)

        self.times.append(self.cur_time)

        # Update current time
        self.cur_time += self.dt

        x, y, vx, vy = self.solver.y

        if x < self.initial_x:
            print("RESETTING ODE")
            self.state = self.initial_x, y, 0, vy
            self.set_integrator()
        else:
            self.state = x, y, vx, vy
        self.positions.append((x, y))


    def setup_gun(self):
        self.bm()

        self.gm()

        self.gev()
        self.jem()

        self.gun_momentum_addition()

        self.gv()

        self.gun_velocity *= 500
        print(self.gun_velocity)


    def gv(self):
        self.gun_velocity = self.gun_momentum / self.gun_weight

    def jem(self):
        self.je_momentum = self.powder_weight * self.mv * 1.7

    def gev(self):
        self.gas_exit_velocity = 1.7 * self.mv

    def bm(self):
        self.bullet_momentum = self.bullet_weight * self.mv

    def gm(self):
        self.gas_momentum = self.powder_weight * self.mv / 2

    def gun_momentum_addition(self):
        self.gun_momentum = self.bullet_momentum + self.gas_momentum + self.je_momentum

    def gun_momentum_multiplication(self):
        self.gun_momentum = self.gun_weight * self.gun_velocity

if __name__ == '__main__':
    title = "Gun simulation"
    win_width = 1000
    win_height = 600
    rounds_per_second = 5
    automatic = False
    released = True
    last_shot = 0
    screen = pygame.display.set_mode((win_width, win_height))
    pygame.display.set_caption(title)
    clock = pygame.time.Clock()

    gun = MyRect(color=GREEN, width=500, height=100)
    text = MyText(color=BLACK)
    center = MyRect(color=RED, width=4, height=4)
    x_axis = MyRect(color=BLACK, width=1000, height=1)
    y_axis = MyRect(color=BLACK, width=1, height=1000)
    my_group = pygame.sprite.Group([x_axis, y_axis, gun, center])

    # setting up simulation
    sim = Simulation()
    initial_state = [500, 250, 0, 0]
    print("""
    Choose a gun:
    1. Remington 700, 11 grain powder, 25 grain .17 Rem. SpHP
    2. Barret M82, 200 grain powder, 750 grain .50 BMG SpBT
    3. M16, 25 grain, 62 grain M855A1 5.56×45mm NATO
    4. Custom
    """)
    choice = input("")
    match choice:
        case "1":
            sim.init(initial_state, 0.712788, 4080.0, 1.61997275, 1231.392)
        case "2":
            sim.init(initial_state, 14.25576, 7127.88, 48.59, 838.8)
        case "3":
            sim.init(initial_state, 1.61997, 3400.0, 4.0175, 961.0)
        case _:
            print("Does not match")
            exit(1)

    while True:
        # 30 fps
        clock.tick(60)

        # update sprite x, y position using values
        # returned from the simulation
        gun.set_pos([sim.state[0], sim.state[1]])

        event = pygame.event.poll()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit(0)

        keys = pygame.key.get_pressed()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_p:
            sim.pause()
            continue
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            sim.resume()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            break
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
            print(f"Switching mode to {'Automatic' if not automatic else 'Semi-Automatic'}")
            automatic = not automatic
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
            rounds_per_second += 1
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
            rounds_per_second = max(1, rounds_per_second - 1)
        elif event.type == pygame.KEYUP and event.key == pygame.K_f:
            released = True
        else:
            pass

        if keys[pygame.K_f]:
            if automatic:
                if (sim.cur_time - last_shot) > 1 / rounds_per_second:
                    sim.shoot = True
                    last_shot = sim.cur_time
            else:
                if released:
                    sim.shoot = True
                    released = False

        if not sim.paused:
            sim.step()
            sim.shoot = False

        screen.fill(WHITE)

        my_group.draw(screen)
        text.draw("Time = %f" % sim.cur_time, screen, (10, 10))
        text.draw("x = %f" % sim.state[0], screen, (10, 40))
        text.draw("y = %f" % sim.state[1], screen, (10, 70))
        text.draw(f"RPS = {rounds_per_second}", screen, (10, 100))
        text.draw(f"Mode = {'Automatic' if automatic else 'Semi-Automatic'}", screen, (10, 130))


        # Update the display
        pygame.display.flip()

