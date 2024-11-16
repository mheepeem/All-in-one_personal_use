from PySide6.QtWidgets import QMessageBox

def show_error_message(parent, title, message):
    QMessageBox.critical(parent, title, message, QMessageBox.Ok)

def show_success_message(parent, title, message):
    QMessageBox.information(parent, title, message, QMessageBox.Ok)