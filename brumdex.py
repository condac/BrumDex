import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QLabel, QCheckBox, QWidget, 
    QScrollArea, QGridLayout, QComboBox, QHBoxLayout
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt


class PokemonApp(QMainWindow):
    SAVE_FILE = "savedata.json"

    def __init__(self, pokemon_data):
        super().__init__()
        self.setWindowTitle("Pokémon Viewer")
        self.setGeometry(100, 100, 800, 600)
        
        self.pokemon_data = pokemon_data
        self.caught_status = self.load_caught_status()

        # Filter and search state
        self.search_text = ""
        self.filter_mode = "All"  # Options: "All", "Caught", "Uncaught"

        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Search and filter bar
        filter_bar = QHBoxLayout()

        search_box = QLineEdit()
        search_box.setPlaceholderText("Search Pokémon by name...")
        search_box.textChanged.connect(self.update_search)
        filter_bar.addWidget(search_box)

        filter_dropdown = QComboBox()
        filter_dropdown.addItems(["All", "Caught", "Uncaught"])
        filter_dropdown.currentTextChanged.connect(self.update_filter)
        filter_bar.addWidget(filter_dropdown)

        main_layout.addLayout(filter_bar)

        # Scroll area for Pokémon grid
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()

        # Grid layout for Pokémon
        self.grid_layout = QGridLayout()
        self.populate_grid()

        scroll_widget.setLayout(self.grid_layout)
        scroll_area.setWidget(scroll_widget)

        main_layout.addWidget(scroll_area)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def populate_grid(self):
        """Populate the grid layout with Pokémon items based on filters."""
        self.grid_layout.setSpacing(10)
        column_count = max(1, self.width() // 150)  # Dynamic columns based on window width
        row, col = 0, 0

        for pokemon in self.pokemon_data:
            name = pokemon["name"]["en"].lower()
            caught = self.caught_status.get(str(pokemon["no"]), False)

            # Apply search filter
            if self.search_text and self.search_text not in name:
                continue

            # Apply caught/uncaught filter
            if self.filter_mode == "Caught" and not caught:
                continue
            if self.filter_mode == "Uncaught" and caught is True:
                continue

            # Create a widget for each Pokémon
            poke_widget = QWidget()
            poke_layout = QVBoxLayout()

            # Pokémon Image (placeholder for now)
            img_label = QLabel()
            pokename = pokemon['name']['en'].lower().replace("♀", "f").replace("♂", "m")
            filename = f"sprites/{pokename}.png"
            if os.path.exists(filename):
                pass
            else:
                print("File not exists", pokename, pokemon['name']['en'])
                filename = f"sprites/placeholder.png"
            pixmap = QPixmap(filename)  # Replace with actual image path
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)

            # Pokémon Name
            name_label = QLabel(pokemon["name"]["en"])
            name_label.setAlignment(Qt.AlignCenter)

            # Checkbox for Caught Status
            checkbox = QCheckBox("Caught")
            checkbox.setChecked(caught)
            checkbox.stateChanged.connect(lambda state, no=pokemon["no"]: self.toggle_caught(state, no))

            # Add to the Pokémon widget layout
            poke_layout.addWidget(img_label)
            poke_layout.addWidget(name_label)
            poke_layout.addWidget(checkbox)
            poke_widget.setLayout(poke_layout)

            # Add the Pokémon widget to the grid
            self.grid_layout.addWidget(poke_widget, row, col)
            col += 1
            if col >= column_count:
                col = 0
                row += 1

    def update_search(self, text):
        """Update search text and refresh the grid."""
        self.search_text = text.lower()
        self.refresh_grid()

    def update_filter(self, mode):
        """Update filter mode and refresh the grid."""
        self.filter_mode = mode
        self.refresh_grid()

    def refresh_grid(self):
        """Clear and repopulate the grid layout."""
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)  # Clear the grid layout
        self.populate_grid()  # Re-populate with updated filters

    def resizeEvent(self, event):
        """Handle window resizing to adapt the grid layout."""
        super().resizeEvent(event)
        self.refresh_grid()

    def toggle_caught(self, state, no):
        self.caught_status[no] = (state == Qt.Checked)
        self.save_caught_status()

    def save_caught_status(self):
        """Save the caught status to a file."""
        with open(self.SAVE_FILE, "w", encoding="utf-8") as file:
            json.dump(self.caught_status, file, indent=4)

    def load_caught_status(self):
        """Load the caught status from a file."""
        if os.path.exists(self.SAVE_FILE):
            with open(self.SAVE_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        return {}


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load Pokémon data from JSON file
    with open("pokemon.json", "r", encoding="utf-8") as file:
        pokemon_data = json.load(file)

    main_window = PokemonApp(pokemon_data)
    main_window.show()
    sys.exit(app.exec_())
