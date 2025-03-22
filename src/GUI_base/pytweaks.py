
from style_themes import THEMES
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

class Zoom:
    """
    Handles zoom functionality for a Matplotlib plot.
    """
    def __init__(self, axes, canvas, color='red'):
        """
        :param axes: The Matplotlib axes to operate on.
        :param canvas: The Matplotlib canvas for drawing updates.
        :param color: Color of the zoom rectangle.
        """
        self.axes = axes
        self.canvas = canvas
        self.color = color
        self.perimeter_lines = []
        self.drag_start = None
        self.drag_end = None
        self.original_lims = None

    def set_color(self, color):
        """
        Sets the color for the zoom rectangle.
        """
        self.color = color

    def set_drag_start(self, x, y):
        """
        Sets the drag start coordinates.
        """
        self.drag_start = (x, y)

    def set_drag_end(self, x, y):
        """
        Sets the drag end coordinates.
        """
        self.drag_end = (x, y)
        self.draw_drag_rectangle()

    def clear_drag_points(self):
        """
        Clears drag start and end points.
        """
        self.drag_start = None
        self.drag_end = None
        self.clear_perimeter_lines()

    def draw_drag_rectangle(self):
        """
        Draws a rectangle on the plot during the drag to show zoom area.
        """
        self.clear_perimeter_lines()
        if self.drag_start and self.drag_end and self.color:
            x_start, y_start = self.drag_start
            x_end, y_end = self.drag_end
            # Draw the perimeter of the rectangle with the selected color
            top_line, = self.axes.plot([x_start, x_end], [y_start, y_start], '--', color=self.color)
            bottom_line, = self.axes.plot([x_start, x_end], [y_end, y_end], '--', color=self.color)
            left_line, = self.axes.plot([x_start, x_start], [y_start, y_end], '--', color=self.color)
            right_line, = self.axes.plot([x_end, x_end], [y_start, y_end], '--', color=self.color)

            self.perimeter_lines = [top_line, bottom_line, left_line, right_line]
            self.canvas.draw()

    def clear_perimeter_lines(self):
        """
        Removes all perimeter lines from the plot and clears the list of stored lines. 
        Also triggers a redraw of the canvas to ensure the plot is updated after the 
        removal of the lines.
        """
        for line in self.perimeter_lines:
            line.remove()  # Remove the line from the plot
        self.perimeter_lines = []
        self.canvas.draw()  # Ensure the canvas updates


    def perform_zoom_in(self):
        """
        Zooms in based on the drag area.
        """
        if self.drag_start and self.drag_end:
            x_start, y_start = self.drag_start
            x_end, y_end = self.drag_end
            x_lower = min(x_start, x_end)
            x_upper = max(x_start, x_end)
            y_lower = min(y_start, y_end)
            y_upper = max(y_start, y_end)
            self.axes.set_xlim(x_lower, x_upper)
            self.axes.set_ylim(y_lower, y_upper)
            self.canvas.draw()
        self.clear_drag_points()

    def perform_zoom_out(self):
        """
        Zooms out to the initial view.
        """
        xlims = [self.original_lims['xlim'][b] for b in self.original_lims['xlim']]
        ylims = [self.original_lims['ylim'][b] for b in self.original_lims['ylim']]
        self.axes.set_xlim(xlims)
        self.axes.set_ylim(ylims)
        self.canvas.draw()
        self.clear_drag_points()

class MouseControl:
    """
    Handles mouse interaction for a Matplotlib plot.
    """
    def __init__(self, canvas, axes, zoom):
        """
        :param canvas: The Matplotlib canvas (FigureCanvas).
        :param axes: The target axes for interaction.
        :param zoom: The Zoom object responsible for the zooming logic.
        """
        self.canvas = canvas
        self.axes = axes
        self.zoom = zoom  # Pass the Zoom instance to MouseControl
        self.dragging = False
        # Connect mouse events
        self.connect_events()

    def connect_events(self):
        """Connects mouse events to handlers."""
        self.canvas.mpl_connect("button_press_event", self.on_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_motion)
        self.canvas.mpl_connect("button_release_event", self.on_release)

    def on_press(self, event):
        """Handles mouse button press event."""
        if event.inaxes == self.axes:
            if event.button == 1:  # Left click (Zoom in)
                self.zoom.set_drag_start(event.xdata, event.ydata)
            elif event.button == 3:  # Right click (Zoom out)
                self.zoom.set_drag_start(event.xdata, event.ydata)

    def on_motion(self, event):
        """Handles mouse motion during drag."""
        if event.inaxes == self.axes and self.zoom.drag_start:
            self.zoom.set_drag_end(event.xdata, event.ydata)

    def on_release(self, event):
        """Handles mouse button release event."""
        if event.inaxes == self.axes:
            if event.button == 1:  # Left click (Zoom in)
                self.zoom.perform_zoom_in()
            elif event.button == 3:  # Right click (Zoom out)
                self.zoom.perform_zoom_out()
            self.zoom.clear_drag_points()

class StyleConfig:
    """A class to manage all style configurations for plots and widgets."""
    
    @staticmethod
    def apply_plot_style(axes, fig, theme="dark"):
        """Apply styles to the plot based on the selected theme."""
        if theme not in THEMES:
            raise ValueError(f"Theme '{theme}' not found. Available themes: {', '.join(THEMES.keys())}")
        
        # Extract plot style settings for the selected theme
        plot_style = THEMES[theme]["plot"]
        
        fig.patch.set_facecolor(plot_style["fig_facecolor"])
        axes.set_facecolor(plot_style["axes_facecolor"])
        axes.grid(color=plot_style["grid_color"], linestyle='--', linewidth=0.5)
        axes.spines['top'].set_color(plot_style["spines_color"])
        axes.spines['right'].set_color(plot_style["spines_color"])
        axes.spines['left'].set_color(plot_style["spines_color"])
        axes.spines['bottom'].set_color(plot_style["spines_color"])
        axes.tick_params(colors=plot_style["tick_color"])
        axes.yaxis.label.set_color(plot_style["label_color"])
        axes.xaxis.label.set_color(plot_style["label_color"])
        axes.title.set_color(plot_style["title_color"])

    @staticmethod
    def apply_widget_style(app, theme="dark"):
        """Apply styles to the Qt widgets based on the selected theme."""
        if theme not in THEMES:
            raise ValueError(f"Theme '{theme}' not found. Available themes: {', '.join(THEMES.keys())}")
        
        # Extract widget style for the selected theme
        widget_style = THEMES[theme]["widget"]
        
        app.setStyleSheet(widget_style)

# Matplotlib Plot Widget
class PlotCanvas(FigureCanvas):
    """
    A custom Matplotlib figure canvas to handle zooming and other interactive features.
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100, theme='dark'):
        """
        Initializes the PlotCanvas with a given parent (QWidget), width, height, and dpi.

        :param parent: The parent QWidget.
        :param width: The width of the figure in inches.
        :param height: The height of the figure in inches.
        :param dpi: The dots per inch of the figure.
        :param theme: The theme to apply to the plot style.
        """
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.theme = theme

        # Initialize the limits dictionary
        self.lims = {'xlim': {'lb': 0, 'ub': 0.1}, 'ylim': {'lb': 0, 'ub': 0.1}}
        self.original_lims = self.lims

        # Apply the plot style based on the theme
        StyleConfig.apply_plot_style(self.axes, self.fig, theme=theme)

        super().__init__(self.fig)
        self.setParent(parent)

        # Initialize zoom functionality
        self.zoom = Zoom(self.axes, self.fig.canvas)
        self.mouse_control = MouseControl(self.fig.canvas, self.axes, self.zoom)

        self.zoom.set_color(THEMES[self.theme]['plot']['label_color'])
        self.plot_colors = THEMES[self.theme]['plot']  # Get the 'plot' dictionary based on selected theme

    def set_label_color(self):
        """
        Retrieves the label color for the selected theme.

        :return: The label color as a string.
        """
        color = self.plot_colors['label_color']
        return color
    

    def store_original_limits(self, original_limits):
        """
        Stores the original limits when a new session is started (or when data is imported).

        :param original_limits: The original limits as a dictionary with keys 'xlim' and 'ylim'.
        """
        self.original_lims = original_limits
        setattr(self.zoom, 'original_lims', self.original_lims)
        self.update_plot_limits(self.original_lims)


    def update_plot_limits(self, value=None, attribute_name=None, limit_type=None):
        """
        Updates plot limits dynamically based on specific arguments or updates all limits if no arguments are passed.

        :param value: The new value for a specific limit. Required if attribute_name and limit_type are provided.
        :param attribute_name: The name of the attribute to update (e.g., 'lb' or 'ub').
        :param limit_type: The limit type to update ('xlim' or 'ylim').
        """
        # If value is a dictionary, it's a batch update
        if isinstance(value, dict):
            # Update all limits in one go
            for lim_type, lim_vals in value.items():
                if lim_type in self.lims:
                    self.lims[lim_type].update(lim_vals)
            # Apply the new limits directly
            self.axes.set_xlim(self.lims['xlim']['lb'], self.lims['xlim']['ub'])
            self.axes.set_ylim(self.lims['ylim']['lb'], self.lims['ylim']['ub'])
            self.draw()
            return

        # Single update case
        if value is not None and attribute_name is not None and limit_type is not None:
            # Update the specific limit in the dictionary
            self.lims[limit_type][attribute_name] = value

            # Apply the updated limits to the plot
            if limit_type == 'xlim':
                self.axes.set_xlim(self.lims['xlim']['lb'], self.lims['xlim']['ub'])
            elif limit_type == 'ylim':
                self.axes.set_ylim(self.lims['ylim']['lb'], self.lims['ylim']['ub'])

            # Redraw the plot after making updates
            self.draw()


