import json
from datetime import datetime
from PySide6.QtCore import Signal
from Controllers.alcool_test_controller import AlcoolTestController
from Controllers.historique_controller import HISTORIQUE_CONTROLLER

class AddHistory:
    error_occurred = Signal(str)

    def __init__(self, arduino_controller=None):
        self.arduino_controller = arduino_controller
        self.save_alcool_value = None
        self.history_controller = HISTORIQUE_CONTROLLER()

        if self.arduino_controller is not None:
            self.arduino_controller.data_received.connect(self.on_data_received)

    def on_data_received(self, line):
        try:
            data = json.loads(line)
            if "alcohol" not in data:
                return

            raw_value = float(data["alcohol"])
            normalized = round(raw_value / 1023.0, 3)
            alert = bool(data.get("alert", False))
            seuil_detection = 400

            if alert and raw_value > seuil_detection:
                self.save_alcool_value = raw_value
            elif normalized > 0:
                self.save_alcool_value = raw_value

        except (json.JSONDecodeError, ValueError):
            pass

        self.save()

    def save(self):
        controller = AlcoolTestController()
        controller.new_alcool_value(datetime.now(), self.save_alcool_value)
        self.save_alcool_value = None

    def get_last_alcool_value(self):
        return self.save_alcool_value
