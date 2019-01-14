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
