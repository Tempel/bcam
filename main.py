import pygtk
pygtk.require('2.0')
import gtk, gobject, cairo
import sys
from events import EVEnum, EventProcessor, ee, ep
from main_window import MainWindow
from state import state

width=640
height=480

class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = { "expose-event": "override" }
    step = 0
    event_consumers = []
    active_event_consumer = None

    def periodic(self):
        ep.process()
        return True

    def save_project(self, *args):
        print "save project"

    def update(self):
        self.queue_draw()

    def scroll_event(self, widget, event):
        print "event:", event
        if event.direction == gtk.gdk.SCROLL_UP:
            ep.push_event(ee.scroll_up, (None))
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            ep.push_event(ee.scroll_down, (None))
    
    def button_press_event(self, widget, event):
        print "button press:", event.button

        if event.button == 1:
            ep.push_event(ee.screen_left_press, (event.x, event.y))

    def key_press_event(self, widget, event):
        print "key press:", event.keyval
        if event.keyval == 65307: # ESC
            ep.push_event(ee.deselect_all, (None))
        elif event.keyval == 65505: # shift
            ep.push_event(ee.shift_press, (None))

    def key_release_event(self, widget, event):
        if event.keyval == 65505: # shift
            ep.push_event(ee.shift_release, (None))

    def button_release_event(self, widget, event):
        if event.button == 1:
            ep.push_event(ee.screen_left_release, (event.x, event.y))

    def motion_notify_event(self, widget, event):
        ep.push_event(ee.pointer_motion, (event.x, event.y))

    # Handle the expose-event by drawing
    def do_expose_event(self, event):
        # Create the cairo context
        #state.offset = (self.allocation.width/2,self.allocation.height/2)
        state.set_screen_offset((self.allocation.width/2, self.allocation.height/2))
        
        offset = state.get_offset()
        scale = state.get_scale()

        cr_gdk = self.window.cairo_create()
        surface = cr_gdk.get_target()
        cr_surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.allocation.width, self.allocation.height)
        cr = cairo.Context(cr_surf)
        
        # Restrict Cairo to the exposed area; avoid extra work
        cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        cr.clip()

        cr.set_source_rgb(0.0, 0.0, 0.0)
        cr.rectangle(0, 0, self.allocation.width, self.allocation.height)
        cr.fill()

        # grid drawing
        cr.set_source_rgb(1.0, 1.0, 1.0)
        step = 1.0
        xsteps = self.allocation.width/state.scale[0]/step
        ysteps = self.allocation.height/state.scale[1]/step
        maxsteps = max(xsteps, ysteps)
        if (maxsteps < 20):
            while (maxsteps < 20):
                if (step/10 == 0):
                    break
                step/=10
                print step
                xsteps = self.allocation.width/state.scale[0]/step
                ysteps = self.allocation.height/state.scale[1]/step
                maxsteps = max(xsteps, ysteps)
        if (maxsteps > 40):
            while (maxsteps > 40):
                step*=10
                xsteps = self.allocation.width/state.scale[0]/step
                ysteps = self.allocation.height/state.scale[1]/step
                maxsteps = max(xsteps, ysteps)

        x = (offset[0]/state.scale[0])%(step)
        y = (offset[1]/state.scale[1])%(step)
        while (x*state.scale[0]<self.allocation.width):
            y = (offset[1]/state.scale[1])%(step)
            while (y*state.scale[1]<self.allocation.height):
                cr.rectangle(x*state.scale[0], y*state.scale[1], 2, 2)
                cr.fill()
                y += step
            x += step

        if state.tool_operations!=None:
            cr.translate(offset[0], offset[1])
            cr.scale(state.scale[0], -state.scale[1])
            for o in state.tool_operations:
                o.draw(cr)
            cr.identity_matrix()
        
        if state.paths!=None:
            cr.translate(offset[0], offset[1])
            cr.scale(state.scale[0], -state.scale[1])
            for p in state.paths:
                p.draw(cr)
            cr.identity_matrix()

        # draw selection box
        if ep.left_press_start != None:
            cr.translate(offset[0], offset[1])
            cr.scale(state.scale[0], -state.scale[1])
            state.settings.select_box_lt.set_lt(cr)
            w = ep.pointer_position[0] - ep.left_press_start[0]
            h = ep.pointer_position[1] - ep.left_press_start[1]
            cr.rectangle(ep.left_press_start[0], ep.left_press_start[1], w, h)
            cr.fill()
            cr.identity_matrix()

        cr_gdk.set_source_surface(cr_surf)
        cr_gdk.paint()

mw = MainWindow(width, height, Screen)
ep.mw = mw

        
# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run():
    mw.run()

if __name__ == "__main__":
    run()
