THEMES = {
    "dark": {
        "plot": {
            "fig_facecolor": "#2E2E2E",
            "axes_facecolor": "#1E1E1E",
            "grid_color": "#555555",
            "spines_color": "#CCCCCC",
            "tick_color": "white",
            "label_color": "white",
            "title_color": "white"
        },
        "widget": """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QLineEdit {
                background-color: #3c3c3c;
                color: #ffffff;
                border: 1px solid #555;
                padding: 2px;
            }
            QLabel {
                color: #ffffff;
            }
            QCheckBox {
                color: #ffffff;
            }
        """
    },
    "light": {
        "plot": {
            "fig_facecolor": "white",
            "axes_facecolor": "white",
            "grid_color": "gray",
            "spines_color": "black",
            "tick_color": "black",
            "label_color": "black",
            "title_color": "black"
        },
        "widget": """
            QWidget {
                background-color: #ffffff;
                color: #000000;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #bbb;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #bbb;
                padding: 2px;
            }
            QLabel {
                color: #000000;
            }
            QCheckBox {
                color: #000000;
            }
        """
    },
    "christmas": {
        "plot": {
            "fig_facecolor": "#004d00",  # Deep green
            "axes_facecolor": "#ffffff",  # White background
            "grid_color": "#d40000",  # Red grid
            "spines_color": "#cc0000",  # Red spines
            "tick_color": "green",  # Green ticks
            "label_color": "#cc0000",  # Red labels
            "title_color": "#004d00"  # Green title
        },
        "widget": """
            QWidget {
                background-color: #ffffff;  # White background for better contrast
                color: #004d00;  # Green text
                font-size: 12pt;
            }
            QPushButton {
                background-color: #d40000;  # Red button
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #004d00;  # Green text
                border: 1px solid #555;
                padding: 2px;
            }
            QLabel {
                color: #cc0000;  # Red labels
            }
            QCheckBox {
                color: #004d00;  # Green checkboxes for contrast
            }
        """
    },
    "halloween": {
        "plot": {
            "fig_facecolor": "#2b0800",  # Dark orange
            "axes_facecolor": "#420d82",  # Purple
            "grid_color": "#f4a300",  # Orange grid
            "spines_color": "#420d82",  # Purple spines
            "tick_color": "black",  # Black ticks
            "label_color": "orange",  # Orange labels
            "title_color": "purple"  # Purple title
        },
        "widget": """
            QWidget {
                background-color: #420d82;  # Purple background for contrast
                color: #ffffff;
                font-size: 12pt;
            }
            QPushButton {
                background-color: #f4a300;  # Orange button
                border: 1px solid #555;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #cc8400;
            }
            QLineEdit {
                background-color: #420d82;  # Purple
                color: #f4a300;  # Orange text for contrast
                border: 1px solid #555;
                padding: 2px;
            }
            QLabel {
                color: #f4a300;  # Orange labels
            }
            QCheckBox {
                color: #ffffff;
            }
        """
    },
    "ferragosto": {
        "plot": {
            "fig_facecolor": "#f4cbb0",  # Sand
            "axes_facecolor": "#ffffff",  # White background
            "grid_color": "#add8e6",  # Light blue grid
            "spines_color": "#e3e3e3",  # Light grey spines
            "tick_color": "#add8e6",  # Light blue ticks
            "label_color": "#b0c4de",  # Light blue labels
            "title_color": "#f4cbb0"  # Sand title
        },
        "widget": """
            QWidget {
                background-color: #f4cbb0;  # Sand background for consistency
                color: #000000;  # Black text for contrast
                font-size: 12pt;
            }
            QPushButton {
                background-color: #e3e3e3;  # Light grey button
                border: 1px solid #bbb;
                padding: 5px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #dcdcdc;
            }
            QLineEdit {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #bbb;
                padding: 2px;
            }
            QLabel {
                color: #add8e6;  # Light blue labels
            }
            QCheckBox {
                color: #add8e6;  # Light blue checkboxes
            }
        """
    }
}
