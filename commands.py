import sublime
import sublime_plugin

from .vintage_relnums import LineModes, VintageRelNums


class VrlToggleLineModeCommand( sublime_plugin.TextCommand ):
    """
    Toggle relative lines in command mode on or off.
    """
    def run( self, edit ):
        controller = VintageRelNums( self.view )
        controller.next_mode()


    def is_enabled( self ):
        return True


    def description( self ):
        if True:
            return "Use native line numbers"

        else:
            return "Use phantom line numbers"


class VrlToggleNativeCommand( sublime_plugin.TextCommand ):
    """
    Toggle native raltive lines in command mode on or off.
    """
    def run( self, edit ):
        controller = VintageRelNums( self.view )
        controller.toggle_native()


    def is_enabled( self ):
        return True


    def description( self ):
        if True:
            return "Use native line numbers"

        else:
            return "Use phantom line numbers"