import platform
import tkinter as tk

if platform.system() == 'Windows':  # Windows


    class Tooltip:
        '''
        It creates a tooltip for a given widget as the mouse goes on it.

        see:

        http://stackoverflow.com/questions/3221956/
               what-is-the-simplest-way-to-make-tooltips-
               in-tkinter/36221216#36221216

        http://www.daniweb.com/programming/software-development/
               code/484591/a-tooltip-class-for-tkinter

        - Originally written by vegaseat on 2014.09.09.

        - Modified to include a delay time by Victor Zaccardo on 2016.03.25.

        - Modified
            - to correct extreme right and extreme bottom behavior,
            - to stay inside the screen whenever the tooltip might go out on
              the top but still the screen is higher than the tooltip,
            - to use the more flexible mouse positioning,
            - to add customizable background color, padding, waittime and
              wraplength on creation
          by Alberto Vassena on 2016.11.05.

          Tested on Ubuntu 16.04/16.10, running Python 3.5.2

        TODO: themes styles support
        '''

        def __init__(self, widget,
                     *,
                     bg='#FFFFEA',
                     pad=(0, 0, 0, 0),
                     text='widget info',
                     waittime=300,
                     wraplength=250):

            self.waittime = waittime  # in miliseconds, originally 500
            self.wraplength = wraplength  # in pixels, originally 180
            self.widget = widget
            self.text = text
            self.widget.bind("<Enter>", self.onEnter)
            self.widget.bind("<Leave>", self.onLeave)
            self.widget.bind("<ButtonPress>", self.onLeave)
            self.bg = bg
            self.pad = pad
            self.id = None
            self.tw = None

        def onEnter(self, event=None):
            self.schedule()

        def onLeave(self, event=None):
            self.unschedule()
            self.hide()

        def schedule(self):
            self.unschedule()
            self.id = self.widget.after(self.waittime, self.show)

        def unschedule(self):
            id_ = self.id
            self.id = None
            if id_:
                self.widget.after_cancel(id_)

        def show(self):
            def tip_pos_calculator(widget, label,
                                   *,
                                   tip_delta=(10, 5), pad=(5, 3, 5, 3)):

                w = widget

                s_width, s_height = w.winfo_screenwidth(), w.winfo_screenheight()

                width, height = (pad[0] + label.winfo_reqwidth() + pad[2],
                                 pad[1] + label.winfo_reqheight() + pad[3])

                mouse_x, mouse_y = w.winfo_pointerxy()

                x1, y1 = mouse_x + tip_delta[0], mouse_y + tip_delta[1]
                x2, y2 = x1 + width, y1 + height

                x_delta = x2 - s_width
                if x_delta < 0:
                    x_delta = 0
                y_delta = y2 - s_height
                if y_delta < 0:
                    y_delta = 0

                offscreen = (x_delta, y_delta) != (0, 0)

                if offscreen:

                    if x_delta:
                        x1 = mouse_x - tip_delta[0] - width

                    if y_delta:
                        y1 = mouse_y - tip_delta[1] - height

                offscreen_again = y1 < 0  # out on the top

                if offscreen_again:
                    # No further checks will be done.

                    # TIP:
                    # A further mod might automagically augment the
                    # wraplength when the tooltip is too high to be
                    # kept inside the screen.
                    y1 = 0

                return x1, y1

            bg = self.bg
            pad = self.pad
            widget = self.widget

            # creates a toplevel window
            self.tw = tk.Toplevel(widget)

            # Leaves only the label and removes the app window
            self.tw.wm_overrideredirect(True)

            win = tk.Frame(self.tw,
                           background=bg,
                           borderwidth=0)
            label = tk.Label(win,
                              text=self.text,
                              justify=tk.LEFT,
                              background=bg,
                              relief=tk.SOLID,
                              borderwidth=1,
                              wraplength=self.wraplength)

            label.grid(padx=(pad[0], pad[2]),
                       pady=(pad[1], pad[3]),
                       sticky=tk.NSEW)
            win.grid()

            x, y = tip_pos_calculator(widget, label)

            self.tw.wm_geometry("+%d+%d" % (x, y))

        def hide(self):
            tw = self.tw
            if tw:
                tw.destroy()
            self.tw = None


    def create_tool_tip(widget, text):
        Tooltip(widget, text=text)

else:
    class ToolTip(object):
        # Taken (with some modification) from http://www.voidspace.org.uk/python/weblog/arch_d7_2006_07_01.shtml#e387
        def __init__(self, widget):
            self.widget = widget
            self.tipwindow = None
            self.id = None
            self.x = self.y = 0

        def showtip(self, text):
            self.text = text
            if self.tipwindow or not self.text:
                return
            x, y, _, cy = self.widget.bbox("insert")
            x = x + self.widget.winfo_rootx() + 27
            tip_length = len(text)
            x -= tip_length if x + tip_length > self.widget.winfo_width() else 0
            y = y + cy + self.widget.winfo_rooty() + 27
            self.tipwindow = tw = tk.Toplevel(self.widget)
            tw.wm_overrideredirect(1)
            tw.wm_geometry("+%d+%d" % (x, y))
            try:
                # For Mac OS
                tw.tk.call("::tk::unsupported::MacWindowStyle",
                           "style", tw._w,
                           "help", "noActivates")
            except tk.TclError:
                pass
            label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                             background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                             font=("Arial", "8"))
            label.pack(ipadx=1)

        def hidetip(self):
            tw = self.tipwindow
            self.tipwindow = None
            if tw:
                tw.destroy()


    def create_tool_tip(widget, text):
        tool_tip = ToolTip(widget)

        def enter(event):
            tool_tip.showtip(text)

        def leave(event):
            tool_tip.hidetip()

        widget.bind('<Enter>', enter)
        widget.bind('<Leave>', leave)