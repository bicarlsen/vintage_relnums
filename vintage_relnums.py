from enum import Enum
import threading

import sublime


class LineModes( Enum ):
    """
    Valid line modes.
    """
    _order_ = 'hybrid relative absolute'

    hybrid   = 'hybrid'
    relative = 'relative'
    absolute = 'absolute'


    def next( self ):
        """
        :returns: Next line mode.
        """
        cls = self.__class__
        members = list( cls )
        index = members.index( self ) + 1
        if index >= len( members ):
            index = 0

        return members[ index ]


class VintageRelNums():
    """
    Base class that controls line numbering.
    """

    settings_file = 'vintage_relnums.sublime-settings'
    view_mode_key = '_vrl_line_mode'
    view_native_key = '_vrl_native_mode'


    def __init__( self, view, settings = None ):
        """
        :param view: sublime.View to operate on.
        :param settings: sublime.Settings. [Default: None]
        """
        self.phantom_id = 'vintage_relnums'
        self.command_mode = 'command_mode'  # vintage command mode
        
        self.view = view

        # setup phantoms
        self.phantom_set = sublime.PhantomSet( self.view, self.phantom_id )

        # debounce
        self.curr_line = None  # currently active line
        self.debounce = None  # debounce timer, threading.Timer

        # settings
        self.settings = (
            sublime.load_settings( self.settings_file )
            if settings is None else
            settings
        )

        if not self.view.settings().has( self.view_mode_key ):
            # initilize view mode if needed
            self.mode = self.settings.get( 'mode' )
        
        if not self.view.settings().has( self.view_native_key ):
            # initilize native if needed
            self.native = self.settings.get( 'native' )

        self.view.settings().add_on_change( self.command_mode, self.update_lines )
        
        # must come last due to dependencies
        self.relative_line_numbers = self.settings.get( 'relative_line_numbers', False )


    @property
    def mode( self ):
        return LineModes( self.view.settings().get( self.view_mode_key ) )

    
    @mode.setter
    def mode( self, mode ):
        # convert mode into a LineModes
        if mode is None:
            mode = LineModes.hybrid

        elif not isinstance( mode, LineModes ):
            mode = LineModes( mode )

        self.view.settings().set( self.view_mode_key, mode.value )
        self.update_lines()


    @property
    def native( self ):
        return (
            self.view.settings().get( self.view_native_key ) and
            self.view.settings().has( 'relative_line_numbers' )
        )


    @native.setter
    def native( self, native ):
        self.view.settings().set( self.view_native_key, native )
        self.update_lines()


    @property
    def style( self ):
        # use double curly braces ( {{ }} )for use in formatted string
        style = ''' 
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
            self.settings.get( 'font_face', self.view.settings().get( 'font_face' ) ),  # default to view's font face
            self.settings.get( 'padding' ),
            self.settings.get( 'current_line_color' ),
            self.settings.get( 'above_line_color' ),
            self.settings.get( 'below_line_color' )
        )

        return style
    

    def in_command_mode( self ):
        """
        :returns: If editor is currently in vintage mode.
        """
        return self.view.settings().get( self.command_mode )


    def remove_phantoms( self ):
        """
        Remove all phantoms.
        """
        self.view.erase_phantoms( self.phantom_id )
        self.phantom_set.update( [] )


    def next_mode( self ):
        """
        Moves to the next line mode.
        """
        self.mode = self.mode.next()
        if ( 
            self.native and 
            ( self.mode is LineModes.relative )
        ):
            # native relative mode doesn't exist
            self.mode = self.mode.next()

        self.update_lines()


    def toggle_native( self, native = None ):
        """
        Set native settings.

        :param native: None to toggle, or value to set.
        """
        if native is None:
            self.native = not self.native

        else:
            self.native = native


    def update_lines( self ):
        """
        Updates the line numbering.
        """
        self.remove_phantoms()

        if self.in_command_mode():
            if self.native:
                relative = ( self.mode is not LineModes.absolute )
                self.view.settings().set( "relative_line_numbers", relative )

            else:
                self.update_phantoms()

        else:
            # not in command mode
            if self.native:
                self.view.settings().set( "relative_line_numbers", self.relative_line_numbers )


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
        if self.mode is LineModes.hybrid:
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
            if self.mode is LineModes.absolute:
                # show absolute line number
                marker = (
                    self.settings.get( 'current_line_marker' )
                    if rel_line == 0 else
                    self.settings.get( 'relative_line_marker' )
                )
                
                show_line = '{:{}>{}}'.format(
                    self.curr_line + rel_line + 1,
                    marker,
                    padding
                )

                if rel_line == 0:
                    classes.append( 'curr_line' )

                elif rel_line < 0:
                    classes.append( 'above_line' )

                else:
                    classes.append( 'below_line' )

                classes.append( 'absolute_line_no' )

            elif ( self.mode is LineModes.hybrid ) and ( rel_line == 0 ):
                # show current line number
                show_line = '{:{}>{}}'.format(
                    self.curr_line + 1,
                    self.settings.get( 'current_line_marker' ),
                    padding
                )

                classes.append( 'curr_line' )
                classes.append( 'absolute_line_no' )

            else:
                show_line = '{:{}>{}}'.format(
                    abs( rel_line ),
                    self.settings.get( 'relative_line_marker' ),
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
        """
        :returns: Current line number (0 indexed).
        """
        active_cursor_pos = self.view.sel()[ -1 ].b
        curr_line = self.view.rowcol( active_cursor_pos )[ 0 ]

        return curr_line
