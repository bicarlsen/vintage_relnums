from threading import Timer

import sublime
import sublime_plugin


class VintageRelNums( sublime_plugin.ViewEventListener ):
    def __init__( self, view ):
        super().__init__( view )

        self.phantom_id = 'vintage_relnums'
        self.span = 100  # how many lines to calculate for relative numbering on each side

        # setup phantoms
        self.phantom_set = sublime.PhantomSet( self.view, self.phantom_id )
        self.remove_phantoms()

        # debounce
        self.debounce = None
        self.debounce_delay = 0.4

        # settings
        self.command_mode = 'command_mode'  # vintage command mode
        self.mode = 'hybrid'
        self.padding = len( str( self.span ) )
        self.style = '''
            <style>
                .absolute_line_no {
                    color: #ccc;
                }

                .relative_line_no {
                    color: #666;
                }
            </style>
        '''

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

        self.debounce = Timer( self.debounce_delay, self.update_phantoms )
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

        rel_start = (
            -cur_line
            if self.span > cur_line else
            -self.span
        )

        max_line = self.view.rowcol( self.view.size() )[ 0 ]
        rel_end = (
            max_line - cur_line + 1
            if cur_line + self.span > max_line else
            self.span + 1
        )

        phantoms = []
        for rel_line in range( rel_start, rel_end ):
            # region
            reg = self.view.text_point( cur_line + rel_line, 0 )
            reg = sublime.Region( reg, reg )

            # content
            if ( self.mode == 'hybrid' ) and ( rel_line == 0 ):
                # show current line number
                show_line = cur_line + 1
                line_class = 'absolute_line_no'

            else:
                show_line = abs( rel_line )
                line_class = 'relative_line_no'

            show_line = '<pre class="{}">{:_>{}}</pre>'.format(
                line_class, show_line, self.padding
            )

            content = '<body>{}<div>{}</div></body>'.format( self.style, show_line )
            phantom = sublime.Phantom( reg, content, sublime.LAYOUT_INLINE )
            phantoms.append( phantom )

        self.phantom_set.update( phantoms )
