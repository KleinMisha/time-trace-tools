from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QLineEdit, QPushButton, QCheckBox, QLabel, QFileDialog, QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal

class PrevNextBTS(QWidget):
    """
    A widget that displays an index and allows user to navigate through a sample
    of given size.

    Parameters
    ----------
    parent : Optional[QWidget]
        The parent of this widget.
    index : Optional[int]
        The initial index, or None if the widget should wait for data before
        handling user input.
    sample_size : int
        The size of the sample to navigate through.
    """
    # Signal emitted when the index changes
    index_changed = pyqtSignal(int)

    def __init__(self, parent=None, index=None, sample_size=0):
        """
        Initialize the PrevNextBTS widget.

        Parameters
        ----------
        parent : Optional[QWidget]
            The parent of this widget.
        index : Optional[int]
            The initial index, or None if the widget should wait for data before
            handling user input.
        sample_size : int
            The size of the sample to navigate through.
        """
        super().__init__(parent)
        # Internal index state, None means "waiting"
        self._index = index
        self.sample_size = sample_size
        self.init_ui()

    def init_ui(self):
        """
        Initializes the UI of the PrevNextBTS widget.

        This includes the buttons, label, and input field for the index. The
        buttons are connected to the `change_index` method, and the input field
        is connected to the `update_index_from_input` method.

        """
        self.layout = QHBoxLayout(self)

        # Previous Button
        self.prev_button = QPushButton('< Previous')
        # Connect to the `change_index` method
        self.prev_button.clicked.connect(lambda: self.change_index('decrease'))
        self.layout.addWidget(self.prev_button)

        # Index Display/Input
        self.index_input = QLineEdit(str(self._index) if self._index is not None else '')
        self.index_input.setFixedWidth(50)  # Optional: set a fixed width
        self.index_input.setAlignment(Qt.AlignCenter)  # Center text
        # Connect to the `update_index_from_input` method
        self.index_input.editingFinished.connect(self.update_index_from_input)
        self.layout.addWidget(self.index_input)

        # Next Button
        self.next_button = QPushButton('Next >')
        self.next_button.clicked.connect(lambda: self.change_index('increase'))
        self.layout.addWidget(self.next_button)

    def change_index(self, direction):
        """
        Change the current index based on the given direction and update the display.

        This method updates the internal index based on the specified direction
        ('increase' or 'decrease'). If the index is incremented or decremented out
        of bounds, a warning message is displayed. If the index is None, indicating
        that the widget is waiting for data, a different warning message is shown.

        Parameters
        ----------
        direction : str
            The direction to change the index, either 'increase' or 'decrease'.

        Emits
        -----
        index_changed : pyqtSignal
            Emitted with the updated index value.
        """
        if self._index is None:
            # Show a warning if the widget is "waiting" for data
            QMessageBox.warning(None, "Waiting for data...", "There's no direction in an empty space.\nLoad your data.")
        elif direction == 'decrease':
            if self._index - 1 >= 0:
                self._index -= 1
            else:
                # Show a warning if the user is trying to go out of bounds
                QMessageBox.warning(None, "Invalid Index", "There's nothing here.\nTry to going in another direction.")
        elif direction == 'increase':
            if self._index + 1 <= self.sample_size:
                self._index += 1
            else:
                # Show a warning if the user is trying to go out of bounds
                QMessageBox.warning(None, "Invalid Index", "There's nothing here.\nTry to going in another direction.")

        # Update the index input display
        self.index_input.setText(str(self._index))
        # Emit the updated index
        self.index_changed.emit(self._index)

    def update_index_from_input(self):
        """
        Updates the internal index from the input field and emits the updated index.

        If the input is invalid (can't be converted to an integer), the input field
        is reset to the current index value.

        Emits
        -----
        index_changed : pyqtSignal
            Emitted with the updated index value.
        """
        try:
            # Try to convert the input to an integer
            new_index = int(self.index_input.text())
            self._index = new_index
            # Emit the updated index
            self.index_changed.emit(self._index)
        except ValueError:
            # Handle invalid input (reset to current _index)
            self.index_input.setText(str(self._index))

    def update_sample_size(self, index=None, sample_size=None):
        """
        Updates the sample size and index of the widget.

        :param index: The new index to display in the input field.
        :param sample_size: The new sample size to update the limits of the widget.
        """
        self.sample_size = sample_size
        # Update the index input display
        self.index_input.setText(str(index))

from PyQt5.QtGui import QDoubleValidator, QIntValidator

# Label - Input Line Edit Matrix 
class Input_QLineEdits(QWidget):
    value_updated = pyqtSignal(float, str, str)  # Signal: value, attribute_name, limit_type

    def __init__(self, rows_config, parent=None):
        super().__init__(parent)
        self.rows = []  # To store the created rows
        self.init_ui(rows_config)

    def init_ui(self, rows_config):
        """
        Initializes the UI for the input matrix.

        :param rows_config: A list of dictionaries containing the configuration for each row.
            Each dictionary should contain the following keys:
                - 'labels': A list of strings to be used as labels for the input fields
                - 'inputs': A list of dictionaries containing the configuration for each input field
                    Each dictionary should contain the following key:
                        - 'valid': The type of validation to apply to the input field ('float' or 'int')
        """
        self.input_matrix = []
        layout = QVBoxLayout()

        for row_config in rows_config:
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(10, 0, 0, 10)
            labels = row_config.get("labels", [])
            inputs = row_config.get("inputs", [])
            input_row = []

            for label_text, input_config in zip(labels, inputs):
                input_line = ValidInputLine(label_text=label_text,valid='float')
                row_layout.addWidget(input_line)
                input_row.append(input_line.input_field)
                # Connect editingFinished to emit signal
                input_line.input_field.editingFinished.connect(
                    lambda field=input_line.input_field, cfg=input_config:
                    self.emit_value_updated(field, cfg)
                )
            self.input_matrix.append(input_row)
            layout.addLayout(row_layout)
        
        
        layout.setSpacing(0)
        self.setLayout(layout)

    def emit_value_updated(self, field, config):
        """
        Emit a signal with updated plot limits based on the input field's value and configuration.

        This method first retrieves and strips the text from the provided input field. It attempts
        to convert this text into a float to be used as the new limit value. If the input field is
        empty, the method reverts to the original plot limits using the provided configuration.

        Parameters
        ----------
        field : QLineEdit
            The input field containing the new limit value as text.
        config : dict
            A dictionary containing configuration details, including:
                - 'attribute_name': The name of the attribute to update (e.g., 'lb' or 'ub').
                - 'limit_type': The type of limit to update ('xlim' or 'ylim').

        Raises
        ------
        ValueError
            If the input value cannot be converted to a float.

        Emits
        -----
        value_updated : pyqtSignal
            Emitted with the new value, attribute name, and limit type if they exist in the config.
        """
        value = field.text().strip()

        # Default values for keys that may or may not exist in the config
        attribute_name = config.get('attribute_name', None)  # Default to None if missing
        limit_type = config.get('limit_type', None)  # Default to None if missing

        # If the field is empty, revert to the original limits
        if not value:
            if attribute_name and limit_type:
                # Safely access original limits
                original_value = self.plot.original_lims.get(limit_type, {}).get(attribute_name, None)
                if original_value is not None:
                    self.plot.update_plot_limits(value=original_value, attribute_name=attribute_name, limit_type=limit_type)
                else:
                    QMessageBox.warning(None, f"Warning: Original limit for {limit_type} -> {attribute_name} not found.")
            return

        # Replace commas with periods to ensure the value is valid for float conversion
        value = value.replace(',', '.')

        try:
            value = float(value)
            # Emit the signal with the new value, attribute, and limit type, only if they exist
            if attribute_name and limit_type:
                self.value_updated.emit(value, attribute_name, limit_type)
            else:
                QMessageBox.warning(None, f"Warning: Missing attribute_name or limit_type in config.")
        except ValueError:
            QMessageBox.warning(None, f"Invalid input: {value}, cannot convert to float.")



class ValidInputLine(QWidget):
    signal_toggled = pyqtSignal(bool)  # Signal to indicate toggle state

    def __init__(self, label_text=None, valid=None, max=None, size=(100, 25), checkbox=None, parent=None):
        """
        Initializes a ValidInputLine widget with a QLabel and a QLineEdit. The QLineEdit is given a QDoubleValidator or QIntValidator
        depending on the 'valid' parameter. If a checkbox is provided, it is added to the layout and connected to the emit_signal method.

        Parameters
        ----------
        label_text : str, optional
            The text to display in the QLabel.
        valid : str, optional
            The type of validation to apply to the input field. Either 'float' or 'int'.
        max : int, optional
            The maximum value for an IntValidator. Ignored if valid is 'float'.
        size : tuple, optional
            The size of the input field as a tuple of (width, height). Defaults to (100, 25).
        checkbox : dict, optional
            A dictionary containing the label and position of a checkbox. If provided, the checkbox is added to the layout.
            The dictionary should contain the following keys:
                'label' : str
                    The text to display on the checkbox.
                'position' : str
                    The position of the checkbox in the layout. Either 'left' or 'right'.
        parent : QWidget, optional
            The parent of this widget. Defaults to None.
        """
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        label = QLabel(label_text)
        label.setFixedWidth(150 if label_text else 0)  # Set fixed width for alignment
        
        self.input_field = QLineEdit()
        self.input_field.setFixedSize(size[0], size[1])
        # Apply a QDoubleValidator to ensure only numeric input
        if valid:
            if valid == 'float':
                validator = FloatValidator()
            elif valid == 'int':
                validator = IntValidator()
                if max:
                    validator.setTop(max)
            self.input_field.setValidator(validator)

        if checkbox:
            self.checkbox = QCheckBox(checkbox['label'])
            self.checkbox.stateChanged.connect(self.emit_signal)
            if checkbox['position'] == 'right':
                widgets = [label, self.input_field, self.checkbox]
            elif checkbox['position'] == 'left':
                widgets = [self.checkbox, label, self.input_field]
            for widget in widgets:
                layout.addWidget(widget, alignment = Qt.AlignLeft)
        else:
            layout.addWidget(label)
            layout.addWidget(self.input_field)
        
        self.setLayout(layout)
    
    def emit_signal(self, state):
        self.signal_toggled.emit(bool(state))  # Emit the signal with the state

class FloatValidator(QDoubleValidator):
    def __init__(self, parent=None):
        """
        Initializes the FloatValidator with a range of -inf to +inf and a precision of 4 decimal places.

        Parameters
        ----------
        parent : Optional[QWidget]
            The parent widget, if any.
        """
        super().__init__(parent)
        self.setRange(-float('inf'), float('inf'), 4)
        self.setNotation(QDoubleValidator.StandardNotation)

class IntValidator(QIntValidator):
    def __init__(self, parent=None, max_value=100000):
        """
        Initialize the IntValidator with a specified maximum value.

        Parameters
        ----------
        parent : Optional[QWidget]
            The parent widget, if any.
        max_value : int
            The maximum allowable integer value. Defaults to 100000.
        """
        super().__init__(parent)
        self.setRange(0, self.setTop(max_value))  # Maximum value is provided by max_value

class Checkbox_Matrix(QWidget):
    boxChecked = pyqtSignal(bool, str)
    def __init__(self, options, parent=None):
        """
        Initialize the Checkbox_Matrix widget.

        Parameters
        ----------
        options : list
            A list of strings that will be used to create the checkboxes.
        parent : QWidget, optional
            The parent widget.
        """
        super().__init__(parent)
        self.options = options + ['All']
        self.init_ui()

    def init_ui(self):
        """
        Initialize the UI of the Checkbox_Matrix widget.

        This function creates a horizontal layout with as many checkboxes as there are options provided in the constructor.
        Each checkbox is connected to the get_checkbox_handler method which emits a signal with the option name when the checkbox is toggled.
        The layout is set as the main layout of this widget.
        """
        layout = QHBoxLayout()
        self.boxes = []
        for option in self.options:
            checkbox = QCheckBox(option)
            checkbox.stateChanged.connect(self.get_checkbox_handler(option))
            self.boxes.append(checkbox)
            layout.addWidget(checkbox)
        self.setLayout(layout)

    def check_all_boxes(self, checked):
        """
        Check or uncheck all boxes based on the value of the 'All' checkbox.
        """
        if checked:
            for cbox in self.boxes:
                cbox.setChecked(True) 

    def get_checkbox_handler(self, option):
        """
        Returns a lambda function that serves as a slot for the stateChanged signal of a checkbox.

        If the option is 'All', it will call the check_all_boxes method with the state of the checkbox.
        If the option is not 'All', it will emit the boxChecked signal with the state of the checkbox and the option.
        """
        if option == 'All':
            return lambda state: self.check_all_boxes(state == Qt.Checked)
        else:
            return lambda state, opt=option: self.boxChecked.emit(state == Qt.Checked, opt)
    
    def get_ticked_boxes(self):
        """
        Returns a list of strings of the ticked boxes.

        Returns
        -------
        list
            A list of strings of the ticked boxes.
        """
        ticked_boxes = [box.text() for box in self.boxes if box.isChecked()]
        return ticked_boxes

class TraceSettingsWidget(QWidget):
    # Define signals to emit updates
    traceIndexChanged = pyqtSignal(str, str)  # Emits new_index, type
    refIndexChanged = pyqtSignal(str, str)  # Emits new_index, type
    autoUpdateToggled = pyqtSignal(bool)
    showAllStateChanged = pyqtSignal(bool)
    ref_toggled = pyqtSignal(bool)

    def __init__(self, sample_size=None, parent=None):
        """
        Initialize the TraceSettingsWidget widget.

        Parameters
        ----------
        sample_size : int, optional
            The size of the sample to be used for the trace index and reference id input fields.
            If not provided, the input fields will not have a max value.
        parent : QWidget, optional
            The parent widget.

        """
        super().__init__(parent)
        
        # Layout for the widget
        main_layout = QVBoxLayout(self)
        traces_info_layout = QHBoxLayout()
        
        self.trace_id_line = self.create_valid_input('Trace nr.', sample_size, 'Show All', 'right', 'sample', self.traceIndexChanged)
        traces_info_layout.addWidget(self.trace_id_line)
        
        self.auto_checkbox = QCheckBox("Auto update")
        self.auto_checkbox.stateChanged.connect(lambda state: self.autoUpdateToggled.emit(state == Qt.Checked))
        traces_info_layout.addWidget(self.auto_checkbox)
        
        main_layout.addLayout(traces_info_layout)
        
        self.ref_id_line = self.create_valid_input('Ref. id', sample_size, 'Ref. sub.', 'left', 'ref', self.refIndexChanged)
        main_layout.addWidget(self.ref_id_line)

    def create_valid_input(self, label_text, max_value, checkbox_label, checkbox_position, emit_type, signal):
        """
        Create a ValidInputLine widget with a QIntValidator and a QCheckBox, and connect the input field and checkbox to the provided signal.

        Parameters
        ----------
        label_text : str
            The text to be displayed as the label for the input field.
        max_value : int, optional
            The maximum value to be accepted by the input field. If not provided, the input field will not have a max value.
        checkbox_label : str
            The text to be displayed on the checkbox.
        checkbox_position : str
            The position of the checkbox relative to the input field. Valid values are 'left' and 'right'.
        emit_type : str
            A string indicating the type of the value that will be emitted by the signal.
        signal : pyqtSignal
            The signal to be emitted when the input field or checkbox is changed.

        Returns
        -------
        ValidInputLine
            The created ValidInputLine widget.
        """
        input_line = ValidInputLine(label_text=label_text, valid='int', max=max_value, 
                                    checkbox={'label': checkbox_label, 'position': checkbox_position})
        input_line.input_field.editingFinished.connect(
            lambda: signal.emit(input_line.input_field.text(), emit_type)
        )
        input_line.signal_toggled.connect(lambda state: self.handle_checkbox_signal(state, signal))
        return input_line

    def handle_checkbox_signal(self, checked, signal):
        signal.emit(checked)