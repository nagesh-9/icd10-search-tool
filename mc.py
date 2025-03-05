import sqlite3
import traceback
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import ScreenManager, Screen
import logging

# Set up logging to capture error messages
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Hardcoded file path for ICD codes
ICD_FILE_PATH = r"C:\Users\Asus\OneDrive\Desktop\Medical Coding App\icd10cm-codes-2025.txt"

# Create and connect to the SQLite database
conn = sqlite3.connect("icd_codes.db")
cursor = conn.cursor()

# Create the ICD Codes table if it doesn't exist
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS icd_codes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    diagnosis TEXT,
    icd_code TEXT
)
''')

# Drop the existing billing_services table if it exists (Solution 1)
cursor.execute('''DROP TABLE IF EXISTS billing_services''')

# Create the billing_services table with the correct schema
cursor.execute(''' 
CREATE TABLE IF NOT EXISTS billing_services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    icd_code TEXT,
    service_name TEXT,
    billing_code TEXT,
    price REAL
)
''')
conn.commit()

# Function to load data from text file into the ICD codes table
def load_data_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
            data = []
            for line in lines:
                line = line.strip()
                if line:
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2:
                        icd_code, diagnosis = parts
                        data.append((diagnosis.strip(), icd_code.strip()))
            cursor.executemany("INSERT INTO icd_codes (diagnosis, icd_code) VALUES (?, ?)", data)
            conn.commit()
    except Exception as e:
        logging.error("Error loading data from file:", exc_info=True)
        print("Error loading data from file:", e)

# Load data from the file (hardcoded path)
load_data_from_file(ICD_FILE_PATH)

# Splash Screen
class SplashScreen(Screen):
    def __init__(self, **kwargs):
        super(SplashScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', spacing=10)
        
        # App Name Label (Big Font)
        self.app_name_label = Label(
            text="Smart Reference ICH",
            font_size='48sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint_y=0.4
        )
        self.layout.add_widget(self.app_name_label)

        # 'Ready?' Button (In the middle)
        self.ready_button = Button(
            text="Ready?",
            size_hint=(None, None),
            size=(200, 50),
            pos_hint={'center_x': 0.5},
            background_color=(0.2, 0.6, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=16
        )
        self.ready_button.bind(on_press=self.transition_to_main)
        self.layout.add_widget(self.ready_button)

        # 'By Nagesh' Label (Smaller Font)
        self.by_nagesh_label = Label(
            text="by Nagesh",
            font_size='20sp',
            color=(1, 1, 1, 1),
            halign='center',
            valign='middle',
            size_hint_y=0.2
        )
        self.layout.add_widget(self.by_nagesh_label)

        self.add_widget(self.layout)

    def transition_to_main(self, instance):
        self.manager.current = 'main_screen'

# Main Screen
class MedicalCodingScreen(Screen):
    def __init__(self, **kwargs):
        super(MedicalCodingScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="horizontal")
        
        # Menu layout (Vertical)
        self.menu_layout = BoxLayout(orientation='vertical', size_hint=(0.4, 1), spacing=10, padding=20)

        # Create buttons for the menu
        self.icd_button = Button(text="ICD", size_hint=(1, None), height=70, background_normal='', background_color=(0.2, 0.5, 0.8, 1), color=(1, 1, 1, 1))
        self.cpt_button = Button(text="CPT", size_hint=(1, None), height=70)
        self.hcpcs_button = Button(text="HCPCS", size_hint=(1, None), height=70)
        self.billing_button = Button(text="Billing", size_hint=(1, None), height=70)
        self.about_button = Button(text="About", size_hint=(1, None), height=70)
        self.exit_button = Button(text="Exit", size_hint=(1, None), height=70)

        # Bind buttons to actions
        self.icd_button.bind(on_press=self.show_icd_search)
        self.billing_button.bind(on_press=self.show_billing_screen)
        self.exit_button.bind(on_press=self.exit_app)

        # Add buttons to the menu layout
        self.menu_layout.add_widget(self.icd_button)
        self.menu_layout.add_widget(self.cpt_button)
        self.menu_layout.add_widget(self.hcpcs_button)
        self.menu_layout.add_widget(self.billing_button)
        self.menu_layout.add_widget(self.about_button)
        self.menu_layout.add_widget(self.exit_button)

        # Add the menu layout to the main layout
        self.layout.add_widget(self.menu_layout)

        # Add an empty area below for the ICD search or About info
        self.content_area = BoxLayout(orientation="vertical", size_hint=(1, 1))
        self.layout.add_widget(self.content_area)

        self.add_widget(self.layout)

    def show_icd_search(self, instance):
        self.manager.current = 'icd_search_screen'

    def show_billing_screen(self, instance):
        self.manager.current = 'billing_screen'

    def exit_app(self, instance):
        App.get_running_app().stop()

# ICD Search Screen
class IcdSearchScreen(Screen):
    def __init__(self, **kwargs):
        super(IcdSearchScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Search input field
        self.input_diagnosis = TextInput(
            hint_text="Type diagnosis here...",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=14,
            padding=[10, 5]
        )
        self.layout.add_widget(self.input_diagnosis)

        # Search button
        self.search_button = Button(
            text="Search",
            size_hint=(1, 0.1),
            background_color=(0.1, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=14
        )
        self.search_button.bind(on_press=self.search_icd_codes)
        self.layout.add_widget(self.search_button)

        # Scrollable results container
        self.scroll = ScrollView(size_hint=(1, 0.8))
        self.result_container = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.result_container.bind(minimum_height=self.result_container.setter('height'))
        self.scroll.add_widget(self.result_container)

        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

    def search_icd_codes(self, instance):
        try:
            diagnoses = self.input_diagnosis.text.strip()
            if not diagnoses:
                self.display_message("⚠ Please enter a diagnosis.", False)
                return

            diagnoses = [d.strip().lower() for d in diagnoses.split(",")]

            cursor = conn.cursor()
            results = {}
            for diagnosis in diagnoses:
                cursor.execute("SELECT DISTINCT diagnosis, icd_code FROM icd_codes WHERE LOWER(diagnosis) LIKE ?", ('%' + diagnosis + '%',))
                matches = cursor.fetchall()
                matches = list(set(matches))  # Remove duplicates
                results[diagnosis] = matches if matches else [("No matching diagnosis found.", "")]

            self.result_container.clear_widgets()
            for diagnosis, matches in results.items():
                self.display_message(f"• Search: [b]{diagnosis.capitalize()}[/b]", True)
                for d, c in matches:
                    if c:
                        self.display_message(f"• [b]{d}[/b]: {c}", False)
                    else:
                        self.display_message(f"• {d}", False)

        except Exception as e:
            logging.error("Error during ICD search:", exc_info=True)
            print("An error occurred during the search:")
            traceback.print_exc()
            self.display_message("[b]❌ An error occurred during the search.[/b]", False)

    def display_message(self, text, is_query):
        bubble = BoxLayout(size_hint_y=None, height=40, padding=5)
        msg_label = Label(
            text=text,
            markup=True,
            halign="left",
            valign="middle",
            color=(0, 0, 0, 1) if is_query else (1, 1, 1, 1)
        )
        if is_query:
            bubble.add_widget(msg_label)
        else:
            msg_label.color = (0.8, 0.2, 0.2, 1)  # Red color for results
            bubble.add_widget(msg_label)

        self.result_container.add_widget(bubble)

# Billing Screen
class BillingScreen(Screen):
    def __init__(self, **kwargs):
        super(BillingScreen, self).__init__(**kwargs)
        self.layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        # Search input field for ICD codes
        self.input_icd = TextInput(
            hint_text="Type diagnosis or ICD code...",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=14,
            padding=[10, 5]
        )
        self.layout.add_widget(self.input_icd)

        # Search button for ICD codes
        self.search_button = Button(
            text="Search ICD Codes",
            size_hint=(1, 0.1),
            background_color=(0.1, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=14
        )
        self.search_button.bind(on_press=self.search_icd_codes)
        self.layout.add_widget(self.search_button)

        # Scrollable results container for ICD codes
        self.scroll_icd = ScrollView(size_hint=(1, 0.4))
        self.result_container_icd = GridLayout(cols=1, size_hint_y=None, spacing=5)
        self.result_container_icd.bind(minimum_height=self.result_container_icd.setter('height'))
        self.scroll_icd.add_widget(self.result_container_icd)
        self.layout.add_widget(self.scroll_icd)

        # Input fields for billing details
        self.input_service = TextInput(
            hint_text="Enter service name...",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=14,
            padding=[10, 5]
        )
        self.layout.add_widget(self.input_service)

        self.input_billing_code = TextInput(
            hint_text="Enter billing code...",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=14,
            padding=[10, 5]
        )
        self.layout.add_widget(self.input_billing_code)

        self.input_price = TextInput(
            hint_text="Enter price...",
            size_hint=(1, 0.1),
            background_color=(0.2, 0.2, 0.2, 1),
            foreground_color=(1, 1, 1, 1),
            font_size=14,
            padding=[10, 5]
        )
        self.layout.add_widget(self.input_price)

        # Save billing details button
        self.save_button = Button(
            text="Save Billing Details",
            size_hint=(1, 0.1),
            background_color=(0.1, 0.5, 0.8, 1),
            color=(1, 1, 1, 1),
            font_size=14
        )
        self.save_button.bind(on_press=self.save_billing_details)
        self.layout.add_widget(self.save_button)

        self.add_widget(self.layout)

    def search_icd_codes(self, instance):
        try:
            query = self.input_icd.text.strip()
            if not query:
                self.display_message("⚠ Please enter a diagnosis or ICD code.", False)
                return

            cursor = conn.cursor()
            cursor.execute("SELECT diagnosis, icd_code FROM icd_codes WHERE diagnosis LIKE ? OR icd_code LIKE ?", 
                           ('%' + query + '%', '%' + query + '%'))
            results = cursor.fetchall()

            self.result_container_icd.clear_widgets()
            if results:
                for diagnosis, icd_code in results:
                    self.display_message(f"Diagnosis: [b]{diagnosis}[/b]\nICD Code: [b]{icd_code}[/b]", False)
            else:
                self.display_message("No matching ICD codes found.", False)

        except Exception as e:
            logging.error("Error during ICD search:", exc_info=True)
            print("An error occurred during the search:")
            traceback.print_exc()
            self.display_message("[b]❌ An error occurred during the search.[/b]", False)

    def save_billing_details(self, instance):
        try:
            # Get input values
            icd_code = self.input_icd.text.strip()
            service_name = self.input_service.text.strip()
            billing_code = self.input_billing_code.text.strip()
            price = self.input_price.text.strip()

            # Validate inputs
            if not all([icd_code, service_name, billing_code, price]):
                self.display_message("⚠ Please fill all fields.", False)
                return

            # Validate price (must be a valid number)
            try:
                price = float(price)
            except ValueError:
                self.display_message("⚠ Price must be a valid number.", False)
                return

            # Insert into billing_services table
            cursor = conn.cursor()
            cursor.execute("INSERT INTO billing_services (icd_code, service_name, billing_code, price) VALUES (?, ?, ?, ?)",
                           (icd_code, service_name, billing_code, price))
            conn.commit()

            # Clear input fields after saving
            self.input_icd.text = ""
            self.input_service.text = ""
            self.input_billing_code.text = ""
            self.input_price.text = ""

            # Display success message
            self.display_message("✅ Billing details saved successfully!", False)

        except sqlite3.IntegrityError as e:
            # Handle database constraints (e.g., unique billing codes)
            logging.error("Database integrity error:", exc_info=True)
            self.display_message("⚠ Error: Billing code must be unique.", False)

        except Exception as e:
            # Log the full error and display a user-friendly message
            logging.error("Error saving billing details:", exc_info=True)
            print("An error occurred while saving billing details:")
            traceback.print_exc()
            self.display_message("[b]❌ An error occurred while saving billing details.[/b]", False)

    def display_message(self, text, is_query):
        bubble = BoxLayout(size_hint_y=None, height=40, padding=5)
        msg_label = Label(
            text=text,
            markup=True,
            halign="left",
            valign="middle",
            color=(0, 0, 0, 1) if is_query else (1, 1, 1, 1)
        )
        if is_query:
            bubble.add_widget(msg_label)
        else:
            msg_label.color = (0.8, 0.2, 0.2, 1)  # Red color for results
            bubble.add_widget(msg_label)

        self.result_container_icd.add_widget(bubble)

# Main App Class
class MedicalApp(App):
    def build(self):
        sm = ScreenManager()

        # Add Screens
        sm.add_widget(SplashScreen(name="splash_screen"))
        sm.add_widget(MedicalCodingScreen(name="main_screen"))
        sm.add_widget(IcdSearchScreen(name="icd_search_screen"))
        sm.add_widget(BillingScreen(name="billing_screen"))

        return sm

if __name__ == "__main__":
    MedicalApp().run()