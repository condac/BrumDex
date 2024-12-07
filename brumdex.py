import sys
import json
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QCheckBox, QWidget, QScrollArea, QGridLayout
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

        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

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
        """Populate the grid layout with Pokémon items."""
        self.grid_layout.setSpacing(10)
        column_count = max(1, self.width() // 150)  # Dynamic columns based on window width
        row, col = 0, 0

        for pokemon in self.pokemon_data:
            # Create a widget for each Pokémon
            poke_widget = QWidget()
            poke_layout = QVBoxLayout()

            # Pokémon Image (placeholder for now)
            img_label = QLabel()
            pokename = pokemon['name']['en'].lower().replace("♀", "f").replace("♂", "m")
            pixmap = QPixmap(f"sprites/{pokename}.png")  # Replace with actual image path
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)

            # Pokémon Name
            name_label = QLabel(pokemon["name"]["en"])
            name_label.setAlignment(Qt.AlignCenter)

            # Checkbox for Caught Status
            checkbox = QCheckBox("Caught")
            checkbox.setChecked(self.caught_status.get(str(pokemon["no"]), False))
            checkbox.stateChanged.connect(lambda state, no=str(pokemon["no"]): self.toggle_caught(state, no))

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

    def resizeEvent(self, event):
        """Handle window resizing to adapt the grid layout."""
        super().resizeEvent(event)
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)  # Clear the grid layout
        self.populate_grid()  # Re-populate with updated column count

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