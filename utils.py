import os
import re

class Utils:
    @staticmethod
    def get_asset_path(filename):
        """Returns the absolute path to an asset file safely."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, 'assets', filename)

    @staticmethod
    def validate_alphabets(input_text):
        """Validate that the input contains only alphabets and spaces."""
        return bool(re.match("^[A-Za-z ]+$", input_text))

    @staticmethod
    def validate_contact(contact):
        """Validate that the contact number is exactly 10 digits."""
        return bool(len(contact) == 10 and contact.isdigit())

class AppStyle:
    """Centralized styling configuration for consistency"""
    BG_COLOR = "#f4f6f9"
    PRIMARY_COLOR = "#007bff"
    SECONDARY_COLOR = "#6c757d"
    DANGER_COLOR = "#dc3545"
    SUCCESS_COLOR = "#28a745"
    TEXT_COLOR = "#333333"
    
    FONT_NORMAL = ("Helvetica", 12)
    FONT_LARGE = ("Helvetica", 14)
    FONT_TITLE = ("Helvetica", 18, "bold")
    FONT_HEADER = ("Helvetica", 24, "bold")
