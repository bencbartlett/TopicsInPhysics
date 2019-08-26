import numpy as np
import vpython as vis
from vpython import vec


class Particle:
    """
    This class represents a gravitational body, such as the Sun, Earth, Moon, or a spaceship
    """

    def __init__(self,
                 name = "Electron",
                 q = 1.6e-19,  # charge of the body in coulomb
                 mass = 9.109e-31,  # mass of body in kg
                 pos = vec(1, 0.0, 0.0),  # x, y, z coordinates of the body in meters
                 vel = vec(0.0, 0.0, 0.0),  # vx, vy, vz  of the body in m/s
                 color = (1.0, 1.0, 1.0)  # color of the body
                 ):
        # Register properties of the body
        self.name = name
        self.q = q
        self.mass = mass
        self.pos = pos
        self.vel = vel
        self.color = color

        # Make vpython visual objects
        self.visual = vis.sphere(pos = pos, color = color, radius = 0.01,
                                 axis = vec(0, 0, 1), make_trail = True, trail_type = "curve", retain = 500)
        self.info = vis.label(pos = self.visual.pos, xoffset = 50, yoffset = -25, height = 9,
                              align = "left", opacity = 0.0, visible = True)

    def update_visuals(self):
        """Updates the position of the visual object to render changes to the screen"""

        # Update sphere position
        self.visual.pos = self.pos

        # Update info text
        radius = self.pos.mag
        speed = self.vel.mag
        self.info.pos = self.visual.pos
        self.info.text = "{}\n|r| = {:.2e}m\n|v| = {:.2e}m/s".format(self.name, radius, speed)


class Cyclotron:
    """
    This class represents a gravitational system which contains many bodies
    """

    def __init__(self, radius = 10.0, bodies = []):
        self.radius = radius
        self.bodies = bodies
        self.base = vis.cylinder(pos = vec(0, 0, -2), axis = vec(0, 0, 1), radius = self.radius,
                                 color = vis.color.gray(0.6))
        self.top_plate = vis.box(pos = vec(0, .5, -1), length = 20, height = .25, width = 1, color = vis.color.red)
        self.bottom_plate = vis.box(pos = vec(0, -.5, -1), length = 20, height = .25, width = 1, color = vis.color.blue)
        self.polarity = "up"
        self.e_field = vec(0, E_mag, 0)
        self.e_indicator = vis.arrow(pos = vec(-11, 0, 0), axis = vec(0, 2, 0), color = vis.color.yellow)
        self.b_field = vec(0, 0, -B_mag)  # 1 mT in -z direction
        self.time_label = vis.label(pixel_pos = vec(0, 0, 0), xoffset = 100, yoffset = -1 * (scene.height - 30),
                                    align = "left", box = True, line = False)

    def polarity_up(self):
        if self.polarity is not "up":
            self.polarity = "up"
            self.e_field = vec(0, E_mag, 0)
            self.e_indicator.rotate(angle = np.pi, axis = vec(0, 0, 1))
            self.top_plate.color = vis.color.red
            self.bottom_plate.color = vis.color.blue

    def polarity_down(self):
        if self.polarity is not "down":
            self.polarity = "down"
            self.e_field = vec(0, -E_mag, 0)
            self.e_indicator.rotate(angle = np.pi, axis = vec(0, 0, 1))
            self.top_plate.color = vis.color.blue
            self.bottom_plate.color = vis.color.red

    def update_visuals(self):
        """Update all visuals for each body in the system"""
        # Update time visuals
        self.time_label.text = "t = {:.3e}".format(t)
        # Update visuals for all bodies
        for body in self.bodies:
            body.update_visuals()


scene = vis.canvas(title = "Cyclotron simulation!   ", width = 1600, height = 900)


def add_widgets(scene, cyclotron):
    """
    Adds menus and sliders to the window to allow you to control the camera and simulation parameters.
    It's not important to understand this function.
    """

    def follow_body(menu):
        scene.camera.follow(cyclotron.bodies[menu.index].visual)

    def change_dt(slider):
        global dt
        dt = 10 ** slider.value
        dt_text.text = "dt={:.2e}s:".format(dt)

    def change_E(slider):
        global E_mag
        E_mag = 10 ** slider.value
        E_text.text = "|E|={:.2e}s:".format(E_mag)

    def change_B(slider):
        global B_mag
        B_mag = 10 ** slider.value
        cyclotron.b_field = vec(0, 0, -B_mag)
        B_text.text = "|B|={:.2e}s:".format(B_mag)

    def toggle_infobox(checkbox):
        for body in cyclotron.bodies:
            body.info.visible = checkbox.checked

    def toggle_controls(checkbox):
        cyclotron.controls_label.visible = checkbox.checked

    vis.wtext(pos = scene.title_anchor, text = "    ")
    vis.wtext(pos = scene.title_anchor, text = "Focus: ")
    vis.menu(pos = scene.title_anchor,
             choices = list(map(lambda body: body.name, cyclotron.bodies)),
             bind = follow_body)
    vis.wtext(pos = scene.title_anchor, text = "    ")

    dt_text = vis.wtext(pos = scene.title_anchor, text = "dt={:.2e}s:".format(dt))
    vis.slider(pos = scene.title_anchor, min = -15, max = -9, value = np.log10(dt), bind = change_dt, length = 200)
    E_text = vis.wtext(pos = scene.title_anchor, text = "|E|={:.2e}N/m:".format(E_mag))
    vis.slider(pos = scene.title_anchor, min = 0, max = 12, value = np.log10(E_mag), bind = change_E, length = 200)
    B_text = vis.wtext(pos = scene.title_anchor, text = "|B|={:.2e}N/m:".format(B_mag))
    vis.slider(pos = scene.title_anchor, min = -4, max = 0, value = np.log10(B_mag), bind = change_B, length = 200)


# Define constants and global variables ================================================================================

# Physical constants
e0 = 8.854e-12  # vacuum permittivity epsilon_0, Farad / meter
mu0 = 4 * np.pi * 10 ** -7  # vacuum permeability mu_0, Tesla meter / amperes

# Global time variables
t = 0  # simulation time in seconds
dt = 1e-14  # simulation timestep in seconds; this value can be changed by the slider
E_mag = 1e7 # N/m
B_mag = 1e-2 # Tesla


def compute_electric_force(particle, cyclotron):
    """
    Computes the electrostatic acceleration of the particle due to the electric fields
    :param particle: a Particle() instance
    :return: a vector (imported as vec) instance which represents the electric force on the particle
    """

    field_region = [cyclotron.bottom_plate.pos.y, cyclotron.top_plate.pos.y]
    if field_region[0] <= particle.pos.y <= field_region[1]:  # field is only present if electron is between the plates
        E = cyclotron.e_field # E is a vec() instance
        q = particle.q # q is a scalar

        # TODO: write this function! (Hint: you can multiply a vec() instance by a scalar)
        # Begin code here ==============================================================================================
        F = E * q
        # End code here ================================================================================================
        return F

    else:  # when you're not between plates there is no E field felt
        return vec(0, 0, 0)


def compute_magnetic_force(particle, cyclotron):
    """
    Computes the electrostatic acceleration of the particle due to the electric fields
    :param particle: a Particle() instance
    :return: a vector (imported as vec) instance which represents the magnetic force on the particle
    """

    radius = particle.pos.mag
    if radius < cyclotron.radius:  # magnetic field is only present inside the cyclotron
        q = particle.q
        v = particle.vel
        B = cyclotron.b_field

        # TODO: write this function! (Hint: you can use vec1.cross(vec2) to compute the cross product)
        # Begin code here ==============================================================================================
        F = q * v.cross(B)
        # End code here ================================================================================================
        return F

    else:  # outside cyclotron there is no B field
        return vec(0, 0, 0)


electron = Particle(color = vis.color.yellow)
cyclotron = Cyclotron(bodies = [electron, ])

add_widgets(scene, cyclotron)

# Main simulation loop
while True:
    # Begin code here ==================================================================================================
    # Update the velocity of the particle by computing acceleration due to electric field and due to magnetic fields

    # TODO: compute acceleration due to E and B
    F_E = compute_electric_force(electron, cyclotron)
    a_E = F_E / electron.mass

    F_B = compute_magnetic_force(electron, cyclotron)
    a_B = F_B / electron.mass

    # TODO: update velocity for the electron
    electron.vel += a_E * dt
    electron.vel += a_B * dt
    # End code here ====================================================================================================

    # TODO: update the position of the electron
    # Begin code here ==================================================================================================
    electron.pos += electron.vel * dt
    # End code here ====================================================================================================

    # Update time and iteration
    t += dt

    # Switch plate polarity when electron passes one of the plates
    if electron.pos.y < cyclotron.bottom_plate.pos.y:
        cyclotron.polarity_up()
    elif electron.pos.y > cyclotron.top_plate.pos.y:
        cyclotron.polarity_down()

    # Update the visuals
    cyclotron.update_visuals()
