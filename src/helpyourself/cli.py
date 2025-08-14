from helpyourself.app_logic import HelpYourselfLogic
import pytest





def main():
    logic = HelpYourselfLogic()
    print("All check-ins:")
    for entry in logic.get_all_checkins():
        print(entry)

if __name__ == "__main__":
    main()


