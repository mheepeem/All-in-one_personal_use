import json
from importlib import import_module
from PySide6.QtWidgets import QStackedWidget

class AppRegistry:
    _apps = {}
    _sub_apps = {}

    @staticmethod
    def register_app(name, widget):
        """Register a main app."""
        AppRegistry._apps[name] = widget

    @staticmethod
    def register_sub_app(parent_name, sub_app_name, widget):
        """Register a sub-app under a parent app."""
        if parent_name not in AppRegistry._sub_apps:
            AppRegistry._sub_apps[parent_name] = {}
        AppRegistry._sub_apps[parent_name][sub_app_name] = widget

    @staticmethod
    def get_app(name):
        """Retrieve a main app."""
        return AppRegistry._apps.get(name)

    @staticmethod
    def get_sub_app(parent_name, sub_app_name):
        """Retrieve a sub-app."""
        return AppRegistry._sub_apps.get(parent_name, {}).get(sub_app_name)

    @staticmethod
    def get_all_apps():
        """Retrieve all main apps."""
        return AppRegistry._apps

    @staticmethod
    def get_all_sub_apps():
        """Retrieve all sub-apps."""
        return AppRegistry._sub_apps


def load_apps_from_config(config_path):
    """Load apps and sub-apps dynamically from a JSON configuration file."""
    with open(config_path, "r") as file:
        config = json.load(file)

    for app_config in config["apps"]:
        try:
            # Resolve the main app's directory
            directory = app_config.get("directory", app_config["class"].lower())
            module_path = f"all_widgets.{directory}"

            # Load the main app
            if app_config["class"] == "QStackedWidget":
                widget = QStackedWidget()
                widget.icon_path = app_config["icon"]
                print(f"Main app registered: {app_config['name']} (as QStackedWidget)")
            else:
                module = import_module(module_path)
                app_class = getattr(module, app_config["class"])
                widget = app_class()
                widget.icon_path = app_config["icon"]
                print(f"Main app registered: {app_config['name']} (as {app_config['class']})")

            # Register the main app
            AppRegistry.register_app(app_config["name"], widget)

            # Load sub-apps with flexibility in directory resolution
            if "sub_apps" in app_config:
                for sub_app_config in app_config["sub_apps"]:
                    try:
                        # Default to `sub_apps` within the main app directory
                        sub_app_directory = sub_app_config.get("directory", "sub_apps")
                        sub_module_path = f"all_widgets.{directory}.{sub_app_directory}"

                        sub_module = import_module(sub_module_path)
                        sub_app_class = getattr(sub_module, sub_app_config["class"])
                        sub_widget = sub_app_class()
                        sub_widget.setObjectName(sub_app_config["name"])

                        AppRegistry.register_sub_app(app_config["name"], sub_app_config["name"], sub_widget)

                        # Add sub-app to the main app if it's a QStackedWidget
                        if isinstance(widget, QStackedWidget):
                            widget.addWidget(sub_widget)
                            print(f"Sub-app registered: {sub_app_config['name']} under {app_config['name']}")
                    except Exception as e:
                        print(f"Error loading sub-app {sub_app_config['name']}: {e}")
        except Exception as e:
            print(f"Error loading app {app_config['name']}: {e}")






