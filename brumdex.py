import sys
import json
import os
import requests
from PyQt5 import QtWidgets, QtCore, QtGui 
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLineEdit, QLabel, QCheckBox, QWidget,
    QScrollArea, QGridLayout, QComboBox, QHBoxLayout, QPushButton, QDialog, QInputDialog, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True) #enable highdpi scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True) #use highdpi icons


import platform
import subprocess
import ctypes
import sys

def get_dpi_settings():
    system = platform.system()

    if system == "Windows":
        return get_dpi_windows()
    elif system == "Linux":
        return get_dpi_linux()
    elif system == "Darwin":  # macOS
        return get_dpi_mac()
    else:
        raise NotImplementedError(f"Unsupported platform: {system}")

def get_dpi_windows():
    try:
        user32 = ctypes.windll.user32
        ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI awareness
        hdc = user32.GetDC(0)
        dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)  # LOGPIXELSX
        user32.ReleaseDC(0, hdc)
        return dpi_x
    except Exception as e:
        print(f"Error getting DPI on Windows: {e}")
        return None

def get_dpi_linux():
    try:
        output = subprocess.run(
            ["xdpyinfo"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        lines = output.stdout.splitlines()
        for line in lines:
            if "dots per inch" in line:
                dpi = int(line.split(":")[1].strip().split("x")[0])
                return dpi
        return 96  # Fallback to default DPI
    except Exception as e:
        print(f"Error getting DPI on Linux: {e}")
        return None

def get_dpi_mac():
    try:
        from AppKit import NSScreen
        from Quartz import CGDisplayScreenSize
        screens = NSScreen.screens()
        for screen in screens:
            description = screen.deviceDescription()
            display_id = description["NSScreenNumber"]
            display_size = CGDisplayScreenSize(display_id)  # millimeters
            width_px = screen.frame().size.width
            dpi = (width_px / (display_size.width / 25.4))
            return dpi
    except Exception as e:
        print(f"Error getting DPI on macOS: {e}")
        return None


def get_scale_factor():

    dpi_x = get_dpi_settings()
    
    # Calculate scale factor (e.g., 96 DPI is 100%, 144 DPI is 150%, etc.)
    scale_factor = dpi_x / 96.0
    return scale_factor
SCALEFACTOR = get_scale_factor()

class PokemonApp(QMainWindow):
    SAVE_DIR = "savefiles"

    def __init__(self, pokemon_data):
        super().__init__()
        self.setWindowTitle("BrumDex Pokémon tracker")
        self.setGeometry(100, 100, 800, 600)
        
        self.pokemon_data = pokemon_data
        os.makedirs(self.SAVE_DIR, exist_ok=True)  # Ensure save directory exists
        self.save_file = None
        self.caught_status = {}
        
        self.search_text = ""
        self.filter_mode = "All"  # Options: "All", "Caught", "Uncaught"
        
        self.redrawwing = False
        self.prevColumncount = 0
        
        self.journeyMobs = ""
        
        
        print(SCALEFACTOR)
        self.initUI()
        self.load_save_file()

    def initUI(self):
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Save file management bar
        save_bar = QHBoxLayout()

        # Dropdown to select save file
        self.save_file_dropdown = QComboBox()
        self.save_file_dropdown.addItems(self.get_save_files())
        self.save_file_dropdown.currentTextChanged.connect(self.change_save_file)
        save_bar.addWidget(self.save_file_dropdown)

        # Button to create a new save file
        new_save_button = QPushButton("New Save File")
        new_save_button.clicked.connect(self.create_new_save_file)
        save_bar.addWidget(new_save_button)

        main_layout.addLayout(save_bar)

        # Search and filter bar
        filter_bar = QHBoxLayout()

        search_box = QLineEdit()
        search_box.setPlaceholderText("Search Pokémon by name...")
        search_box.textChanged.connect(self.update_search)
        search_box.setClearButtonEnabled(True)
        filter_bar.addWidget(search_box)

        filter_dropdown = QComboBox()
        filter_dropdown.addItems(["All", "Caught", "Uncaught", "JourneyMap"])
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
        
        bottom_bar = QHBoxLayout()
        
        # Label with number of pokemons cought
        self.counter_label = QLabel()
        self.counter_label.setText("Hej")
        bottom_bar.addWidget(self.counter_label)
        
        # Label with connection info
        self.journeyStatus_label = QLabel()
        self.journeyStatus_label.setText("JHej")
        
        bottom_bar.addWidget(self.journeyStatus_label)
        main_layout.addLayout(bottom_bar)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        self.timerJM = QTimer()
        self.timerJM.timeout.connect(self.getJourneyMap)
        self.timerJM.start(5000)

    def get_save_files(self):
        """Get a list of save files in the save directory."""
        return [f[:-5] for f in os.listdir(self.SAVE_DIR) if f.endswith(".json")]

    def change_save_file(self, save_file):
        """Change the active save file."""
        self.save_file = save_file
        self.load_save_file()

    def create_new_save_file(self):
        """Create a new save file."""
        new_save_file, ok = QInputDialog.getText(self, "New Save File", "Enter a name for the new save file:")
        if ok and new_save_file:
            new_save_file = new_save_file.strip()
            if new_save_file in self.get_save_files():
                self.show_error("Save file already exists.")
            else:
                self.save_file = new_save_file
                self.caught_status = {}
                self.save_caught_status()
                self.save_file_dropdown.addItem(new_save_file)
                self.save_file_dropdown.setCurrentText(new_save_file)

    def load_save_file(self):
        """Load the caught status from the selected save file."""
        if not self.save_file:
            self.save_file = self.save_file_dropdown.currentText()

        file_path = os.path.join(self.SAVE_DIR, f"{self.save_file}.json")
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                self.caught_status = json.load(file)
        else:
            self.caught_status = {}

        self.refresh_grid(force=True)

    def save_caught_status(self):
        """Save the caught status to the current save file."""
        if not self.save_file:
            self.show_error("No save file selected.")
            return

        file_path = os.path.join(self.SAVE_DIR, f"{self.save_file}.json")
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.caught_status, file, indent=4)
        
        print("save ",f"{self.save_file}.json",  self.caught_status)

    def show_error(self, message):
        """Show an error dialog."""
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Error")
        error_layout = QVBoxLayout()
        error_layout.addWidget(QLabel(message))
        close_button = QPushButton("Close")
        close_button.clicked.connect(error_dialog.close)
        error_layout.addWidget(close_button)
        error_dialog.setLayout(error_layout)
        error_dialog.exec_()

    def populate_grid(self):
        """Populate the grid layout with Pokémon items."""
        self.grid_layout.setSpacing(0)
        column_count = int(max(1, self.width() // (150*SCALEFACTOR) ) ) # Dynamic columns based on window width
        row, col = 0, 0
        self.prevColumncount = column_count
        
        for pokemon in self.pokemon_data:
            name = pokemon["name"]["en"].lower()
            caught = self.caught_status.get(str(pokemon["no"]), False)

            # Apply search and filter logic
            if self.search_text and self.search_text.lower() not in f"#{int(pokemon['no']):04} {pokemon['name']['en'].lower()}":
                continue

            if self.filter_mode == "Caught" and not caught:
                continue
            if self.filter_mode == "Uncaught" and caught is True:
                continue
            pokename = pokemon['name']['en'].lower().replace("♀", "f").replace("♂", "m").replace("'", "").replace(" ", "").replace(".", "").replace(" ", "").replace("é", "e").replace("-", "")
            
            if self.filter_mode == "JourneyMap":
                # print("kollar om ", str(pokemon["no"]), "finns i", self.journeyMobs)
                pokenr = f"{int(pokemon['no']):04}"
                if pokenr not in self.journeyMobs:
                    continue
            # if self.filter_mode == "JourneyMap" and pokename not in self.journeyMobs:
            #     continue
            # print(name, caught)
            # Create a widget for each Pokémon
            poke_widget = QWidget()
            poke_layout = QVBoxLayout()
            poke_layout.setSpacing(0)
            # Pokémon Image (placeholder for now)
            img_label = QLabel()
            filename = f"sprites/{pokename}.png"
            if os.path.exists(filename):
                pass
            else:
                print("File not exists", pokename, pokemon['name']['en'])
                filename = f"sprites/placeholder.png"
            pixmap = QPixmap(filename)  # Replace with actual image path
            pixmap = pixmap.scaled(int(100*SCALEFACTOR), int(100*SCALEFACTOR), Qt.KeepAspectRatio)
            img_label.setPixmap(pixmap)
            img_label.setAlignment(Qt.AlignCenter)


            font = QFont()
            font.setPointSize(13)  # Set the font size
            
        
            # Pokémon Number
            number_label = QLabel(f"#{int(pokemon['no']):04}")
            number_label.setAlignment(Qt.AlignCenter)
            number_label.setFont(font)
            
            # Pokémon Name
            name_label = QLabel(f"{pokemon['name']['en']}")
            name_label.setAlignment(Qt.AlignCenter)
            name_label.setFont(font)

            # Checkbox for Caught Status
            checkbox = QCheckBox("Caught")
            checkbox.setChecked(caught)
            checkbox.stateChanged.connect(lambda state, no=pokemon["no"]: self.toggle_caught(state, no))

            # Add to the Pokémon widget layout
            poke_layout.addWidget(img_label)
            poke_layout.addWidget(number_label)
            poke_layout.addWidget(name_label)
            poke_layout.addWidget(checkbox)
            poke_widget.setLayout(poke_layout)

            # Add the Pokémon widget to the grid
            self.grid_layout.addWidget(poke_widget, row, col)
            col += 1
            if col > column_count:
                col = 0
                row += 1
        verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        poke_widget = QWidget()
        poke_layout = QVBoxLayout()
        poke_layout.addItem(verticalSpacer)
        poke_widget.setLayout(poke_layout)
        self.grid_layout.addWidget(poke_widget, row+1, col)
        horizontalSpacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Minimum)
        poke_widget = QWidget()
        poke_layout = QVBoxLayout()
        poke_layout.addItem(horizontalSpacer)
        poke_widget.setLayout(poke_layout)
        self.grid_layout.addWidget(poke_widget, row+1, column_count+1)

    def update_search(self, text):
        """Update search text and refresh the grid."""
        self.search_text = text.lower()
        self.refresh_grid(force=True)

    def update_filter(self, mode):
        """Update filter mode and refresh the grid."""
        self.filter_mode = mode
        self.refresh_grid(force=True)

    def refresh_grid(self, force=False):
        """Clear and repopulate the grid layout."""
        column_count = max(1, self.width() // 150)
        if (column_count == self.prevColumncount and force == False):
            self.redrawwing = False
            return
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)  # Clear the grid layout
        self.populate_grid()
        
        self.updateCounter()
        self.redrawwing = False

    def updateCounter(self):
        # Count catched pokemons
        counter = 0
        # print("count", self.caught_status)
        for pok in self.caught_status:
            # print("count", pok)
            if self.caught_status[pok] == True:
                counter += 1
        self.counter_label.setText(f"Catched pokemons: {counter}")
        
    def resizeEvent(self, event):
        """Handle window resizing to adapt the grid layout."""
        super().resizeEvent(event)
        
        if self.redrawwing:
            pass
        else:
            QTimer.singleShot(500, self.refresh_grid)
            self.redrawwing = True
        

    def toggle_caught(self, state, no):
        # print("Cought ", state, no)
        self.caught_status[str(no)] = (state == Qt.Checked)
        self.save_caught_status()
        self.updateCounter()
        # print("toggle_caught", self.caught_status)


    def getJourneyMap(self):
        
        if self.filter_mode == "JourneyMap":
            try:
                # Fetch the sprite
                response = requests.get("http://localhost:8080/data/animals")
                response.raise_for_status()  # Raise an exception for HTTP errors
                self.journeyMobs = ""
                for line in response.content.decode().splitlines():
                    if "cobblemon" in line:
                        self.journeyMobs += line
                        if "shiny" in line:
                            print("SHINY !!!!!!!!!!!", line)
                print(f"Updated journeymap")
                self.journeyStatus_label.setText(f"Updated journeymap")
                # print(self.journeyMobs)
                self.refresh_grid(force=True)

            except requests.RequestException as e:
                print(f"Failed to update journeymap")
                self.journeyStatus_label.setText(f"Failed to update journeymap")
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Arial", 9)  # You can specify the font family and size
    app.setFont(font)
    
    # Load Pokémon data from JSON file
    with open("pokemon.json", "r", encoding="utf-8") as file:
        pokemon_data = json.load(file)

    main_window = PokemonApp(pokemon_data)
    main_window.show()
    sys.exit(app.exec_())
