def linux_exec(name, x=0, y=0):
    '''
    position specified monitor to (x, y) coordinates using xrandr
    '''
    import subprocess
    print("Executing: xrandr --output {} --pos {}x{}".format(name, x, y).split(" "))
    subprocess.run("xrandr --output {} --pos {}x{}".format(name, x, y).split(" "))

def windows_exec(name, x=0, y=0):
    '''
    position specified monitor to (x, y) coordinates using win32 api
    '''
    import win32api
    import win32con
    import pywintypes

    devmode = pywintypes.DEVMODEType()

    devmode.Position_x = int(x)
    devmode.Position_y = int(y)

    devmode.Fields = win32con.DM_POSITION

    win32api.ChangeDisplaySettingsEx(name, devmode, 0)