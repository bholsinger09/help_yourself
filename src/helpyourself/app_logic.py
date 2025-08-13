class HelpYourselfLogic:
    def __init__(self):
        self.status = "Not Checked In"
        self.button_label = "Check In"

    def check_in(self):
        self.status = "Checked In"
        self.button_label = "Take Health Check"

    def take_health_check(self):
        self.status = "Health Check Complete"
        self.button_label = "Checked In"  # fixed to match test
