import threading

import sublime
import sublime_plugin


class VintageRelNums( sublime_plugin.ViewEventListener ):
    def __init__( self, view ):
        """
        :param view: sublime.View to operate on.
        """
        super().__init__( view )

        self.phantom_id = 'vintage_relnums'
        self.command_mode = 'command_mode'  # vintage command mode

        # setup phantoms
        self.phantom_set = sublime.PhantomSet( self.view, self.phantom_id )
        self.remove_phantoms()

        # debounce
        self.curr_line = None  # currently active line
        self.debounce = None  # debounce timer, threading.Timer

        # settings
        self.settings = sublime.load_settings( 'vintage_relnums.sublime-settings' )
        # TODO [0]: Redraw phantoms on settings change
        # self.settings.add_on_change( self.update_lines )

        self.mode = self.settings.get( 'mode' )
        self.relative_line_numbers = self.settings.get( 'relative_line_numbers', False )

        # styles
        # use double curly braces ( {{ }} )for use in formatted string
        self.style = '''
            <style>
                * {{
                    font-family: {};
                    padding-right: {};
                }}

                .curr_line {{
                    color: {};
                }}

                .above_line {{
                    color: {};
                }}

                .below_line {{
                    color: {};
                }}
            </style>
        '''.format(
                self.settings.get( 'font_face', view.settings().get( 'font_face' ) ),  # default to view's font face
                self.settings.get( 'padding' ),
                self.settings.get( 'curr_line_color' ),
                self.settings.get( 'above_line_color' ),
                self.settings.get( 'below_line_color' )
            )

        self.view.settings().add_on_change( self.command_mode, self.update_lines )


    def on_activated( self ):
        """
        Inserts phantoms when first entering vintage mode.
        """
        self.update_lines()


    def on_selection_modified_async( self ):
        """
        Modifies line numbers when cursor is moved.
        """
        if not self.in_command_mode():
            self.remove_phantoms()
            return


        if self.get_current_line() == self.curr_line:
            # cursor's line number did not change
            return

        if self.debounce is not None:
            # cancel currently running
            self.debounce.cancel()

        self.debounce = threading.Timer(
            self.settings.get( 'debounce_delay' ),
            self.update_lines
        )
        
        self.debounce.start()


    def in_command_mode( self ):
        """
        :returns: If editor is currently in vintage mode.
        """
        return self.view.settings().get( self.command_mode )


    def remove_phantoms( self ):
        """
        Remove all phantoms.
        """
        self.view.erase_phantoms( self.phantom_id )  # remove previous phantom sets
        self.phantom_set.update( [] )


    def update_lines( self ):
        native = (
            self.settings.get( 'native' ) and
            ( int( sublime.version() ) >= 4000 )
        )
        
        if self.in_command_mode():
            if native:
                self.view.settings().set( "relative_line_numbers", True )

            else:
                self.update_phantoms()

        else:
            # not in command mode
            if native:
                self.view.settings().set( "relative_line_numbers", self.relative_line_numbers )

            else:
                self.remove_phantoms()


    def update_phantoms( self ):
        """
        Updates phantoms to match current cursor position.
        """
        if (
            ( self.debounce is not None ) and
            ( threading.current_thread() != self.debounce )
        ):
            # invalid thread, missed cancellation
            # required because on quick scrolling
            # some of the debounce timers do not get cancelled.
            return

        self.curr_line = self.get_current_line()

        # calculate padding
        min_padding = len( str( self.settings.get( 'span' ) ) )
        if self.mode == 'hybrid':
            line_no = self.curr_line + 1  # curr_line is zero indexed
            line_len = len( str( line_no ) )
            padding = max( line_len, min_padding )

        else:
            padding = min_padding

        span = self.settings.get( 'span' )
        rel_start = (
            -self.curr_line
            if span > self.curr_line else
            -span
        )

        max_line = self.view.rowcol( self.view.size() )[ 0 ]
        rel_end = (
            max_line - self.curr_line + 1
            if self.curr_line + span > max_line else
            span + 1
        )

        phantoms = []
        for rel_line in range( rel_start, rel_end ):
            # region
            reg = self.view.text_point( self.curr_line + rel_line, 0 )
            reg = sublime.Region( reg, reg )

            # content
            classes = []
            if ( self.mode == 'hybrid' ) and ( rel_line == 0 ):
                # show current line number
                show_line = '{:{}>{}}'.format(
                    self.curr_line + 1,
                    self.settings.get( 'curr_line_marker' ),
                    padding
                )

                classes.append( 'curr_line' )
                classes.append( 'absolute_line_no' )

            else:
                show_line = '{:{}>{}}'.format(
                    abs( rel_line ),
                    self.settings.get( 'rel_line_marker' ),
                    padding
                )

                if rel_line == 0:
                    classes.append( 'curr_line' )

                elif rel_line < 0:
                    classes.append( 'above_line' )

                else:
                    classes.append( 'below_line' )

                classes.append( 'relative_line_no' )


            classes.append( 'vintage_relnums' )
            show_line = '<span class="{}">{}</span>'.format(
                ' '.join( classes ), show_line
            )

            content = '<body>{}<div>{}</div></body>'.format( self.style, show_line )
            phantom = sublime.Phantom( reg, content, sublime.LAYOUT_INLINE )
            phantoms.append( phantom )

        self.phantom_set.update( phantoms )
        self.debounce = None


    def get_current_line( self ):
        active_cursor_pos = self.view.sel()[ -1 ].b
        curr_line = self.view.rowcol( active_cursor_pos )[ 0 ]

        return curr_line
