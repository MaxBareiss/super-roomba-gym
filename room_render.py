# super-roomba-gym
# Copyright (C) 2019 Max Bareiss

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from super_roomba.envs.room import Room
import cairo

if __name__ == "__main__":
    r = Room()
    for i in range(100):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1000, 1000)
        ctx = cairo.Context(surface)
        ctx.set_source_rgba(0, 0, 0, 1)
        ctx.rectangle(0, 0, 1000, 1000)
        ctx.fill()
        r.generate()
        #ctx.scale(5 / 1000, 5 / 1000)
        ctx.scale(1000 / 5, 1000 / 5)
        ctx.translate(1, 1)
        r.render(ctx)
        surface.write_to_png("{:02d}.png".format(i))
