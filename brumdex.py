import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox, QWidget, QScrollArea
)
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class PokemonApp(QMainWindow):
    def __init__(self, pokemon_data):
        super().__init__()
        self.setWindowTitle("Pokémon Viewer")
        self.setGeometry(100, 100, 600, 800)
        
        self.pokemon_data = pokemon_data
        self.caught_status = {poke["no"]: False for poke in pokemon_data}
        
        self.initUI()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Scroll area for Pokémon list
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout()

        for pokemon in self.pokemon_data:
            item_layout = QHBoxLayout()
            
            # Display Pokémon Image (placeholder for now)
            img_label = QLabel()
            pixmap = QPixmap("bulbasaur.png")  # Replace with actual image path
            pixmap = pixmap.scaled(80, 80, Qt.KeepAspectRatio)
            img_label.setPixmap(pixmap)
            
            # Pokémon Name
            name_label = QLabel(f"{pokemon['no']}. {pokemon['name']['en']}")
            
            # Checkbox for Caught Status
            checkbox = QCheckBox("Caught")
            checkbox.stateChanged.connect(lambda state, no=pokemon["no"]: self.toggle_caught(state, no))
            
            item_layout.addWidget(img_label)
            item_layout.addWidget(name_label)
            item_layout.addWidget(checkbox)
            scroll_layout.addLayout(item_layout)

        scroll_widget.setLayout(scroll_layout)
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)

        main_layout.addWidget(scroll_area)
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def toggle_caught(self, state, no):
        self.caught_status[no] = (state == Qt.Checked)
        print(f"Pokémon {no} caught status: {self.caught_status[no]}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Load Pokémon data from JSON file
    with open("pokemon.json", "r", encoding="utf-8") as file:
        pokemon_data = json.load(file)

    main_window = PokemonApp(pokemon_data)
    main_window.show()
    sys.exit(app.exec_())
