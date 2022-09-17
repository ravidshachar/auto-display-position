import screeninfo
import tkinter as tk
import subprocess

class Display():
    def __init__(self, window, canvas, rectangle, name="", x = "", y = "", width_mm = None, height_mm = None):
        self.window = window
        self.canvas = canvas
        self.rectangle = rectangle
        
        self.name = name
        self.x = x
        self.y = y
        self.width_mm = width_mm
        self.height_mm = height_mm

    # get the average between the rectangle top y and bottom y coordinates
    def adjusted_y(self):
        coords = self.canvas.coords(self.rectangle)
        return (coords[1] + coords[3]) / 2

class Main(tk.Tk):
    def __init__(self, monitors, line_width):
        super().__init__()
        self.displays = []
        for m in monitors:
            window = tk.Toplevel()
            window.geometry("{}x{}+{}+{}".format(m.width, m.height, m.x, m.y))
            window.attributes("-fullscreen", True)

            c = tk.Canvas(window, width=m.width, height=m.height)
            r = c.create_rectangle(0, 
                                   (m.height - line_width) / 2, 
                                   m.width, 
                                   (m.height + line_width) / 2, 
                                   fill="black")

            c.bind("<Button-1>", lambda e: self.on_click(e), add="+")
            c.bind("<B1-Motion>", lambda e: self.on_drag(e), add="+")
            window.bind("<Control-s>", lambda e: self.save(e, window))
            window.bind("<Escape>", lambda e: self.destroy())

            display = Display(window, 
                              c, 
                              r,
                              name=m.name,
                              x=m.x,
                              y=m.y,
                              width_mm=m.width_mm,
                              height_mm=m.height_mm)
            self.displays.append(display)
        tk.Label(c, text="Press <Ctrl-S> to save and <Escape> to quit", font=(None, 50)).place(x=1, y=1)
        self.withdraw()

    # initialize monitors to be at the same location from the top
    def init_monitors(self, monitors):
        for m in monitors:
            subprocess.run("xrandr --output {} --pos {}x{}".format(m.name, m.x, 0).split(" "))

    def on_click(self, e):
        # Get the currently focused canvas
        c = self.get_canvas_by_window(self.focus_get())
        # Find the rectangle in the canvas
        selected = c.find_overlapping(e.x-10, e.y-10, e.x+10, e.y+10)
        if selected:
            c.selected = selected[-1]  # select the top-most item
            c.startxy = (e.x, e.y) # This is used to track how much the mouse moved
            print(c.selected, c.startxy)
        else:
            c.selected = None

    def on_drag(self, e):
        # Get the currently focused canvas
        c = self.get_canvas_by_window(self.focus_get())
        if c.selected:
            # calculate distance moved from last position
            dy = e.y-c.startxy[1]
            # move the rectangle
            c.move(c.selected, 0, dy)
            # update last position
            c.startxy = (e.x, e.y)

    def save(self, e, c):
        # Initialize first display to y=0
        d = self.displays[0]
        subprocess.run("xrandr --output {} --pos {}x{}".format(d.name, d.x, 0).split(" "))

        # Setup all displays
        for i in range(1, len(self.displays)):
            # This is the difference in pixels between the two displays
            calc = self.displays[0].adjusted_y() - self.displays[i].adjusted_y()
            tk.Label(c, text=calc, font=(None, 50)).place(x=1, y=151) # show new y

            d = self.displays[i]

            # set second display relatively to the first display
            subprocess.run("xrandr --output {} --pos {}x{}".format(d.name, d.x, calc).split(" "))

    # Get the canvas associated with a certain Toplevel object
    def get_canvas_by_window(self, window):
        for d in self.displays:
            if d.window == window:
                return d.canvas
        return None

    def mainloop(self):
        for d in self.displays:
            d.canvas.pack()
        super().mainloop()

if __name__ == "__main__":
    # get physical (or virtual) monitor info
    monitors = screeninfo.get_monitors() 
    
    main = Main(monitors, 10)
    main.mainloop()