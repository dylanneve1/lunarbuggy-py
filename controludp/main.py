from controludp_movement import movement
from controludp_soil import soil_sample

if __name__ == '__main__':
    while True:
        print("Please Choose a function")
        print("1: movement")
        print("2: soil sampling")
        print("exit: Exit the program")
        
        choice = input("-> ")
        match choice:
            case '1':
                movement()
            case '2':
                soil_sample()
            case 'exit':
                print("Program Terminating")
                break
            case _:
                print("Invalid Input Command")
