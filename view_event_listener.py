import threading

import sublime
import sublime_plugin

from .vintage_relnums import VintageRelNums


class VrlViewEventListener( sublime_plugin.ViewEventListener ):
    """
    ViewEventListener to control line numbering on view changes.
    """
    def __init__( self, view ):
        """
        :param view: sublime.View to operate on.
        """
        super().__init__( view )
        self.controller = VintageRelNums( self.view )


    def on_activated( self ):
        """
        Inserts phantoms when first entering vintage mode.
        """
        self.controller.update_lines()


    def on_selection_modified_async( self ):
        """
        Modifies line numbers when cursor is moved.
        """
        ctrl = self.controller
        if not ctrl.in_command_mode():
            ctrl.remove_phantoms()
            return

        if ctrl.get_current_line() == ctrl.curr_line:
            # cursor's line number did not change
            return

        if ctrl.debounce is not None:
            # cancel currently running
            ctrl.debounce.cancel()

        ctrl.debounce = threading.Timer(
            ctrl.settings.get( 'debounce_delay' ),
            ctrl.update_lines
        )
        
        ctrl.debounce.start()
