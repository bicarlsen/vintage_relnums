# Vintage Relative Numbering
Relative numbering for Sublime's Vintage mode.

![Example](example.png)

## Install Instructions

Ensure that [Vintage mode](https://www.sublimetext.com/docs/3/vintage.html) is enabled for Sublime.

In `Command` or `Visual` mode you will have control over the line numbering style.

### From Package Control (Recommended)

1. Install [Package Control](https://packagecontrol.io/installation).

2. Run the “Package Control: Install Package” command.

3. Find and install the "Vintage Relative Lines" plugin.

4. Restart Sublime Text if there are issues.

### Manually

1. Navigate to Sublime's Packages directory. 

    This can be found by opening up Sublime's console (``Ctrl + ` (backtick)``, or `View > Show Console` ), and run `sublime.packages_path()`.

2. Place the `vintage_relnums` folder inside the Packages directory. 

    You can do this by cloning or downloading these files.
    For cloning, from the Packages directory run `git clone https://github.com/bicarlsen/vintage_relnums.git` in a console.

## Commands

Two commands are provided with the plugin.

### Toggle Line Mode
**Command:** `vrl_toggle_line_mode`

**Default Key Map:** `ctrl + alt + l`

Cycles through available line numbering modes.

+ When using phantoms these modes are `hybrid`, `relative`, and `absolute`.

+ When using native numbering the modes are `hybrid` and `absolute`.

### Toggle Native
**Command:** `vrl_toggle_native`

**Default Key Map:** `ctrl + alt + n`

Toggles between using phantoms and native line numbering, if available.

## Settings
Change settings for the plugin by opening the `Preferences > Package Settings > Vintage Relative Lines` menu, and clicking on `Settings - User`. This opens up the user settings file. By clicking on `Settings - Default` the default settings file is opened, and all the settings with an explanation are provided.


## Keybindings
The default key bindings for the package's commands are given in the [**Commands** section](#commands). These bindings can be modified by openeing the `Preferences > Package Settings > Vintage Relative Lines` menu and clicking on `Key Bindings – Default`. One can add to the deafult key bindings in the `Key Bindings – User` file, which is also accesible via `Preferences > Key Bindings`.

## Helping Out

Please feel free to help out and imporve this plugin. It is my first sublime plugin so is fairly simple and should be easy to improve.

## Acknowledgements

I used [OdatNurd's Plugin 101 tutorial videos](https://youtube.com/playlist?list=PLGfKZJVuHW91zln4ADyZA3sxGEmq32Wse) to get started. If you're interested in learning how to develop Sublime plugins it is a great starting point.