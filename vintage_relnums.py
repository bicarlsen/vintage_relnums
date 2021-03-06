from threading import Timer

import sublime
import sublime_plugin


class VintageRelNums( sublime_plugin.ViewEventListener ):
    def __init__( self, view ):
        super().__init__( view )

        self.phantom_id = 'vintage_relnums'
        self.command_mode = 'command_mode'  # vintage command mode

        # setup phantoms
        self.phantom_set = sublime.PhantomSet( self.view, self.phantom_id )
        self.remove_phantoms()

        # debounce
        self.debounce = None

        # settings
        default_settings = {
            'mode': 'hybrid',
            'span': 100,  # how many lines to calculate for relative numbering on each side

            'curr_line_color':  '#90a959',
            'above_line_color': '#a63d40',
            'below_line_color': '#6494aa',

            'curr_line_marker': '*',
            'rel_line_marker':  '.',

            'debounce_delay': 0.4
        }

        self.settings = default_settings

        self.mode = self.settings[ 'mode' ]
        self.min_padding = len( str( self.settings[ 'span' ] ) )

        # styles
        # use double curly braces ( {{ }} )for use in formatted string
        self.style = '''
            <style>
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
            self.settings[ 'curr_line_color' ],
            self.settings[ 'above_line_color' ],
            self.settings[ 'below_line_color' ]
        )

        self.view.settings().add_on_change( self.command_mode, self.update_phantoms )


    def on_activated( self ):
        self.update_phantoms()


    def on_selection_modified_async( self ):
        if not self.in_command_mode():
            self.remove_phantoms()
            return

        if self.debounce is not None:
            # cancel currently running
            self.debounce.cancel()

        self.debounce = Timer( self.settings[ 'debounce_delay' ], self.update_phantoms )
        self.debounce.start()
        self.debounce.join()
        self.debounce = None

    def in_command_mode( self ):
        return self.view.settings().get( self.command_mode )


    def remove_phantoms( self ):
        self.view.erase_phantoms( self.phantom_id )  # remove previous phantom sets
        self.phantom_set.update( [] )


    def update_phantoms( self ):
        if not self.in_command_mode():
            # not in command mode
            self.remove_phantoms()
            return

        active_cursor_pos = self.view.sel()[ -1 ].b
        cur_line = self.view.rowcol( active_cursor_pos )[ 0 ]

        # calculate padding
        if self.mode == 'hybrid':
            padding = max( len( str( cur_line ) ), self.min_padding )

        else:
            padding = self.min_padding

        span = self.settings[ 'span' ]
        rel_start = (
            -cur_line
            if span > cur_line else
            -span
        )

        max_line = self.view.rowcol( self.view.size() )[ 0 ]
        rel_end = (
            max_line - cur_line + 1
            if cur_line + span > max_line else
            span + 1
        )

        phantoms = []
        for rel_line in range( rel_start, rel_end ):
            # region
            reg = self.view.text_point( cur_line + rel_line, 0 )
            reg = sublime.Region( reg, reg )

            # content
            classes = []
            if ( self.mode == 'hybrid' ) and ( rel_line == 0 ):
                # show current line number
                show_line = '{:{}>{}}'.format(
                    cur_line + 1,
                    self.settings[ 'curr_line_marker' ],
                    padding
                )

                classes.append( 'curr_line' )
                classes.append( 'absolute_line_no' )

            else:
                show_line = '{:{}>{}}'.format(
                    abs( rel_line ),
                    self.settings[ 'rel_line_marker' ],
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
