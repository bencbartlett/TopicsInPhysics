import numpy as np
import vpython as vis
from vpython import vec


class Body:
    """
    This class represents a gravitational body, such as the Sun, Earth, Moon, or a spaceship
    """

    def __init__(self,
                 name = "Orbital Body",
                 mass = 1.0,  # mass of the body in kg
                 x = 0.0, y = 0.0, z = 0.0,  # x, y, z coordinates of the body in meters
                 vx = 0.0, vy = 0.0, vz = 0.0,  # vx, vy, vz  of the body in m/s
                 radius = 1e8,  # radius of the body in meters
                 color = (1.0, 1.0, 1.0)  # color of the body
                 ):
        # Register properties of the body
        self.name = name
        self.mass = mass
        self.x = x
        self.y = y
        self.z = z
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.color = color
        self.radius = radius

        # Make vpython visual objects
        self.visual = vis.sphere(pos = vec(x, y, z), color = color, radius = radius,
                                 axis = vec(0, 0, 1), make_trail = True, trail_type = "curve", retain = 500)
        self.info = vis.label(pos = self.visual.pos, xoffset = 50, yoffset = -25, height = 9,
                              align = "left", opacity = 0.0, visible = True)

    def update_visuals(self):
        """
        Updates the position of the visual object to render changes to the screen
        """

        # Update sphere position
        self.visual.pos = vec(self.x, self.y, self.z)

        # Update info text
        radius = np.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)
        speed = np.sqrt(self.vx ** 2 + self.vy ** 2 + self.vz ** 2)
        self.info.pos = self.visual.pos
        self.info.text = "{}\n|r| = {:.2e}m\n|v| = {:.2e}m/s".format(self.name, radius, speed)


class Star(Body):
    """
    Orbital body representing a star, which acts as a light source
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Give the star a special texture and make it a light source
        self.visual.texture = "http://i.imgur.com/yoEzbtg.jpg"
        self.visual.emissive = True
        vis.local_light(pos = self.visual.pos, color = vec(1, 1, 1))


class Planet(Body):
    """
    Orbital body representing a planet
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.visual.emissive = False
        self.visual.shininess = 0.0


class Moon(Body):
    """
    Orbital body representing a moon; by specifying parent_body you can provide coordinates and velocities
    relative to the parent body, e.g. moon = Moon(parent_body = earth, ...)
    """

    def __init__(self, *args, parent_body = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.visual.emissive = False
        self.visual.shininess = 0.0

        # Register parent body and adjust coordinates and velocities accordingly
        self.parent_body = parent_body
        if self.parent_body is not None:
            self.x = self.parent_body.x + self.x
            self.y = self.parent_body.y + self.y
            self.z = self.parent_body.z + self.z
            self.vx = self.parent_body.vx + self.vx
            self.vy = self.parent_body.vy + self.vy
            self.vz = self.parent_body.vz + self.vz
            self.visual.clear_trail() # clear the trail so you don't get a visual bug


class Spaceship(Body):
    """
    Orbital body representing a spaceship (or non-planet/star/moon object)
    """

    def __init__(self,
                 *args,
                 **kwargs):
        super().__init__(*args, **kwargs)
        self.visual = vis.pyramid(pos = vec(self.x, self.y, self.z), color = self.color,
                                  size = 1e5 * vec(1.0, .5, .5),  # size needs to be big enough to render
                                  axis = vec(-1, 0, 0), make_trail = True, trail_type = "curve", retain = 500)


class SolarSystem:
    """
    This class represents a gravitational system which contains many bodies
    """

    def __init__(self, bodies = []):
        # Register the solar system bodies
        self.bodies = bodies

        # Make some visual objects to display in the scene
        self.time_label = vis.label(pixel_pos = vec(0, 0, 0), xoffset = 100, yoffset = -1 * (scene.height - 30),
                                    align = "left", box = True, line = False)
        self.controls_label = vis.label(pixel_pos = vec(0, 0, 0), xoffset = 300, yoffset = -1 * (scene.height - 71),
                                        text = "Controls\nScroll: zoom camera\nRight click + drag: orbit camera",
                                        align = "left", box = True, line = False, visible = False)

    def update_visuals(self):
        """
        Update all visuals for each body in the system
        """

        # Update time visuals
        day = int(t / (60 * 60 * 24))
        self.time_label.text = "t = {:.3e} (Day {})".format(t, day)

        # Update visuals for all bodies
        for body in self.bodies:
            body.update_visuals()


scene = vis.canvas(title = "Solar system simulation!   ", width = 1600, height = 900)


def add_widgets(scene, solar_system):
    """
    Adds menus and sliders to the window to allow you to control the camera and simulation parameters.
    It's not important to understand this function.
    """

    def follow_body(menu):
        scene.camera.follow(solar_system.bodies[menu.index].visual)

    def change_dt(slider):
        global dt
        dt = 10 ** slider.value
        dt_text.text = "dt={:.2e}s:".format(dt)

    def toggle_infobox(checkbox):
        for body in solar_system.bodies:
            body.info.visible = checkbox.checked

    def toggle_controls(checkbox):
        solar_system.controls_label.visible = checkbox.checked

    vis.wtext(pos = scene.title_anchor, text = "    ")
    vis.wtext(pos = scene.title_anchor, text = "Focus: ")
    vis.menu(pos = scene.title_anchor,
             choices = list(map(lambda body: body.name, solar_system.bodies)),
             bind = follow_body)
    vis.wtext(pos = scene.title_anchor, text = "    ")

    dt_text = vis.wtext(pos = scene.title_anchor, text = "dt={:.2e}s:".format(dt))
    vis.slider(pos = scene.title_anchor,
               min = 0, max = 6,
               value = np.log10(dt),
               bind = change_dt)
    vis.wtext(pos = scene.title_anchor, text = "    ")
    vis.checkbox(pos = scene.title_anchor, text = "Enable infoboxes", checked = True, bind = toggle_infobox)
    vis.wtext(pos = scene.title_anchor, text = "    ")
    vis.checkbox(pos = scene.title_anchor, text = "Show controls", checked = False, bind = toggle_controls)


# Define constants and global variables ================================================================================

# Color constants for your convenience
COLOR_BLACK = vis.color.black
COLOR_WHITE = vis.color.white
COLOR_RED = vis.color.red
COLOR_GREEN = vis.color.green
COLOR_BLUE = vis.color.blue
COLOR_DARK_BLUE = vec(0, 0, 0.6)
COLOR_LIGHT_BLUE = vec(0.31, 0.49, 1.0)
COLOR_YELLOW = vis.color.yellow
COLOR_CYAN = vis.color.cyan
COLOR_MAGENTA = vis.color.magenta
COLOR_ORANGE = vis.color.orange
COLOR_ORANGE_RED = vec(1, 0.3, 0)
COLOR_ORANGE_YELLOW = vec(1, 0.8, 0)
COLOR_PURPLE = vis.color.purple
COLOR_LIGHT_GREY = vis.color.gray(0.7)
COLOR_DARK_GREY = vis.color.gray(0.5)

# Physical constants
G = 6.674e-11  # gravitational constant, m^3 kg^-1 s^-2
AU = 1.496e11  # 1AU = 1.496 * 10^11 meters: you can also define your orbital parameters in AU instead of meters

# Global time variables
t = 0  # simulation time in seconds
dt = 100  # simulation timestep in seconds; this value can be changed by the slider


def compute_acceleration(body1, body2):
    """
    Computes the gravitational acceleration of body2 exerted upon body 1
    :param body1: a Body() instance
    :param body2: a Body() instance
    :return: a tuple representing ax, ay, az exerted on body 1
    """
    # TODO: write this function!
    # Begin code here ==================================================================================================
    dx = body1.x - body2.x
    dy = body1.y - body2.y
    dz = body1.z - body2.z
    distance = np.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    a_mag = - G * body2.mass / distance ** 2
    ax = a_mag * dx / distance
    ay = a_mag * dy / distance
    az = a_mag * dz / distance
    # End code here ====================================================================================================
    return ax, ay, az


# TODO: specify the solar system!
# You can find a list of planetary orbital parameters at https://nssdc.gsfc.nasa.gov/planetary/factsheet/index.html
# Begin code here ======================================================================================================
sun = Star(
        name = "Sun",
        mass = 1.989e30,
        x = 0, y = 0, z = 0,
        vx = 0, vy = 0, vz = 0,
        radius = 695510e3,
        color = COLOR_YELLOW)
# mercury = Planet(
#         name = "Mercury",
#         mass = 0.330e24,
#         x = 69.8e9, y = 0, z = 0,
#         vx = 0, vy = 47.36e3, vz = 0,
#         radius = 2439e3,
#         color = COLOR_DARK_GREY)
# venus = Planet(
#         name = "Venus",
#         mass = 4.87e24,
#         x = 108.9e9, y = 0, z = 0,
#         vx = 0, vy = 34.79e3, vz = 0,
#         radius = 6051.8e3,
#         color = COLOR_ORANGE)
# earth = Planet(
#         name = "Earth",
#         mass = 5.97e24,
#         x = 152.1e9, y = 0, z = 0,
#         vx = 0, vy = 29.29e3, vz = 0,
#         radius = 6378e3,
#         color = COLOR_BLUE)
# moon = Moon(
#         name = "Moon",
#         parent_body = earth,
#         mass = 0.073e24,
#         x = 0.405e9, y = 0, z = 0,
#         vx = 0, vy = 0.970e3, vz = 0,
#         radius = 1738e3,
#         color = COLOR_LIGHT_GREY)
# mars = Planet(
#         name = "Mars",
#         mass = 0.642e24,
#         x = 249.63e9, y = 0, z = 0,
#         vx = 0, vy = 21.97e3, vz = 0,
#         radius = 6378e3,
#         color = COLOR_RED)
# jupiter = Planet(
#         name = "Jupiter",
#         mass = 1898e24,
#         x = 816.62e9, y = 0, z = 0,
#         vx = 0, vy = 12.44e3, vz = 0,
#         radius = 66854e3,
#         color = COLOR_ORANGE_RED)
# saturn = Planet(
#         name = "Saturn",
#         mass = 568e24,
#         x = 1514.5e9, y = 0, z = 0,
#         vx = 0, vy = 9.09e3, vz = 0,
#         radius = 54364e3,
#         color = COLOR_ORANGE_YELLOW)
# uranus = Planet(
#         name = "Uranus",
#         mass = 86.8e24,
#         x = 3003.6e9, y = 0, z = 0,
#         vx = 0, vy = 6.49e3, vz = 0,
#         radius = 24963e3,
#         color = COLOR_LIGHT_BLUE)
# neptune = Planet(
#         name = "Neptune",
#         mass = 102e24,
#         x = 4545.7e9, y = 0, z = 0,
#         vx = 0, vy = 5.37e3, vz = 0,
#         radius = 24341e3,
#         color = COLOR_CYAN)
# pluto = Planet(
#         name = "Pluto",
#         mass = 102e24,
#         x = 7375.9e9, y = 0, z = 0,
#         vx = 0, vy = 3.71e3, vz = 0,
#         radius = 1186e3,
#         color = COLOR_LIGHT_GREY)

r_earth = 149.6e9
r_jwst = 151.1e9
v_earth = 29.8e3
v_jwst = v_earth * r_jwst / r_earth

earth_copy = Planet(
        name = "Earth",
        mass = 5.97e24,
        x = r_earth, y = 0, z = 0,
        vx = 0, vy = v_earth, vz = 0,
        radius = 6378e3,
        color = COLOR_BLUE)



jwst = Spaceship(
        name = "JWST",
        mass = 1e6,
        x = r_jwst, y = 0, z = 0,
        vx = 0, vy = v_jwst, vz = 0,
        color = COLOR_MAGENTA)

solar_system = SolarSystem(bodies = [
    sun,
    # mercury,
    # venus,
    # earth,
    # moon,
    # mars,
    # jupiter,
    # saturn,
    # uranus,
    # neptune,
    # pluto,
    earth_copy,
    jwst
])
# End code here ========================================================================================================

add_widgets(scene, solar_system)

# Main simulation loop
while True:
    # Update the velocity of each body by computing acceleration to every other body
    for body1 in solar_system.bodies:
        for body2 in solar_system.bodies:
            if body1 != body2:
                # Compute the acceleration from each other body on body1
                ax, ay, az = compute_acceleration(body1, body2)

                # TODO: update vx, vy, vz for each planet
                # Begin code here ======================================================================================
                body1.vx += ax * dt
                body1.vy += ay * dt
                body1.vz += az * dt
                # End code here ========================================================================================

    # Update the position of each body
    for body in solar_system.bodies:
        # TODO: update x, y, z for each planet
        # Begin code here ==============================================================================================
        body.x += body.vx * dt
        body.y += body.vy * dt
        body.z += body.vz * dt
        # End code here ================================================================================================

    # Update time and iteration
    t += dt

    # Update the visuals
    solar_system.update_visuals()
