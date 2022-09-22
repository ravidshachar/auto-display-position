import screeninfo
import tkinter as tk
from executors import linux_exec, windows_exec
import platform

class Display():
    def __init__(self, window, canvas, rectangle, name="", x = "", y = ""):
        self.window = window
        self.canvas = canvas
        self.rectangle = rectangle
        
        self.name = name
        self.x = x
        self.y = y

    # get the average between the rectangle top y and bottom y coordinates
    def adjusted_y(self):
        coords = self.canvas.coords(self.rectangle)
        return (coords[1] + coords[3]) / 2

class Main(tk.Tk):
    def __init__(self, monitors, line_width):
        super().__init__()
        self.displays = []
        if platform.system() == "Windows":
            self.executor = windows_exec
        elif platform.system() == "Linux":
            self.executor = linux_exec
        else:
            raise Exception("Unsupported platform. This tool only supports Windows and Linux")

        line_height = min([m.height for m in monitors])
        self.initialize_displays(monitors, line_height, line_width)

        tk.Label(self.displays[-1].canvas, 
                 text="Press <Ctrl-S> to save and <Escape> to quit", 
                 font=(None, 50)
                ).place(x=1, y=1)
        self.withdraw()

    def initialize_displays(self, monitors, line_height, line_width):
        print(monitors)
        for m in monitors:
            window = tk.Toplevel()
            window.geometry("{}x{}+{}+{}".format(m.width, m.height, m.x, m.y))
            
            if platform.system() == "Windows":
                window.state("zoomed")
            else:
                window.attributes("-fullscreen", True)

            c = tk.Canvas(window, width=m.width, height=m.height)
            r = c.create_rectangle(0, 
                                   (line_height - line_width) / 2, 
                                   m.width, 
                                   (line_height + line_width) / 2, 
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
                              y=m.y)
            self.displays.append(display)

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
        self.executor(d.name, d.x, 0)

        # Setup all displays
        for i in range(1, len(self.displays)):
            # This is the difference in pixels between the two displays
            calc = self.displays[0].adjusted_y() - self.displays[i].adjusted_y()
            tk.Label(c, text=calc, font=(None, 50)).place(x=1, y=151) # show new y

            d = self.displays[i]
            # set second display relatively to the first display
            self.executor(d.name, d.x, calc)

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
