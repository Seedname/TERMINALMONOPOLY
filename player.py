import os
import socket
from time import sleep
from colorama import Fore, Style, Back
import style as s
from screenspace import Player as ss
from modules import PlayerModules as m

game_running = False
text_dict = {}
active_terminal = 1
sockets = (socket.socket, socket.socket)
ADDRESS = ""
PORT = 0
balance = 0
properties = 0


def get_graphics():
    """Grab text from ascii.txt and split into dictionary"""
    global text_dict
    text_dict = s.get_graphics()

def initialize():
    """
    Initialize client receiver and sender network sockets, attempts to connect to a Banker by looping, then handshakes banker.

    ### This may be unnecessary: fix as necessary.
    Creates two sockets, a receiver and sender at the same address.

    Updates the ADDRESS and PORT class variables by taking in player input. Calls itself until a successful connection. 
    Then calls handshake() to confirm player is connected to Banker and not some other address. 

    Parameters: None
    Returns: None
    """
    global sockets, ADDRESS, PORT
    os.system("cls")
    print("Welcome to Terminal Monopoly, Player!")
    s.print_w_dots("Initializing client socket connection")     
    client_receiver = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   
    client_sender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockets = (client_receiver, client_sender)
    ADDRESS = input("Enter Host IP: ")
    PORT = input("Enter Host Port: ")
    s.print_w_dots("Press enter to connect to the server...", end='')
    input()
    try:
        client_receiver.connect((ADDRESS, int(PORT)))
        print(Fore.BLUE+"Connection successful!"+Style.RESET_ALL)
    except:
        n = input(Fore.RED+"Connection failed. Type 'exit' to quit or press enter to try again.\n"+Style.RESET_ALL)
        if n == "exit":
            quit()
        else:
            initialize()
    try:
        handshake(client_receiver)
    except Exception as e:
        print(e)
        n = input(Fore.RED+"Handshake failed. Type 'exit' to quit or press enter to try again.\n"+Style.RESET_ALL)
        if n == "exit":
            quit()
        else:
            initialize()

    s.print_w_dots("Attempting to connect to Banker's receiver...")
    sleep(1)
    try:
        sockets[1].connect((ADDRESS, int(PORT)+1))
    except Exception as e:
        print(e)
        s.print_w_dots("Failed connecting. ")
    
def handshake(sock: socket.socket) -> str:
    """
    Used in ensuring the client and server are connected and can send/receive messages. 
    Parameters:
    sock (socket.socket) Client socket to receive message on.

    Returns:
    string representing the "Welcome to the game!" confirmation message.
    """
    # Sockets should send and receive relatively simultaneously. 
    # As soon as the client connects, the server should send confirmation message.
    message = sock.recv(1024).decode('utf-8')
    print(message)
    if message == "Welcome to the game!":
        sock.send(bytes("Connected!", 'utf-8'))
        return message
    else:
        s.print_w_dots(Fore.RED+"Handshake failed. Reason: Connected to wrong foreign socket.")

def calculate() -> None:
    """
    Helper method for calling calculator() in modules.py. Updates screen accordingly. 
    Parameters: None
    Returns: None
    """
    # Initial comment in active terminal
    ss.update_quadrant(active_terminal, "Enter a single operation equation:")
    ss.print_screen()
    # All other work is done on the work line (bottom of the screen)
    ss.update_quadrant(active_terminal, m.calculator())
    ss.print_screen()

def balance() -> None:
    """
    Display player's cash, assets, etc. 

    Parameters: None
    Returns: None
    """
    pass

def list_properties() -> None:
    """
    Temporary function to list all properties on the board by calling the property list stored in ascii.txt.
    Can be reworked to add color and better formatting.
    
    Parameters: None
    Returns: None
    """
    ss.update_quadrant(active_terminal, text_dict.get('properties'))
    ss.print_screen()

def set_terminal(n: int) -> None:
    """
    Updates global "active_terminal" variable for all terminal updating needs. Also updates the active terminal
    in screenspace module, and prints the new screen.
    
    Parameters: 
    n (int) number [1-4] of which terminal to set as active. 
    
    Returns: None
    """
    global active_terminal
    active_terminal = n
    ss.update_active_terminal(n)
    ss.print_screen()

def game_input() -> None:
    """
    Main loop for ALL client-server interactions. Displays the gameboard. 
    Should take over "get_input" as input handler during this time, until stdIn == "back" 
    indicating return to terminal screen.

    Parameters: None
    Returns: None
    """
    stdIn = ""
    board = ["" for i in range(35)]
    try:
        sockets[1].send('request_board'.encode())
        sleep(0.1)

        size = sockets[1].recv(4)
        board_pieces = ""
        board_pieces = sockets[1].recv(int.from_bytes(size)).decode()
        sleep(0.1)
        board = m.make_board(board_pieces)
        ss.clear_screen()
        ss.print_board(board) ## Failing line
    except Exception as e:
        ss.overwrite(Fore.RED + "Something went wrong. The Banker may not be ready to start the game.\n")
        print(e)
    
    while(stdIn != "back"):
        print(Fore.GREEN+"Monopoly Screen: Type 'back' to return to the main menu.")
        stdIn = input(Back.LIGHTWHITE_EX+Fore.BLACK+'\r').lower().strip()
        if stdIn == "back":
            ss.print_screen()
            # Breaks the loop, returns to get_input() 
            return
        elif stdIn == "exit" or stdIn.isspace() or stdIn == "":
            # On empty input make sure to jump back on the console line instead of printing anew
            ss.overwrite(Style.RESET_ALL + "\n\r")
        else:
            # ss.overwrite('\n' + ' ' * ss.WIDTH)
            ss.overwrite(Style.RESET_ALL + Fore.RED + "Invalid command. Type 'help' for a list of commands.")

    # sockets[1].close()
    # ss.print_screen()

# Probably want to implement threading for printing and getting input.
def get_input():
    """
    Main loop for input handling while in the terminal screen. Essentially just takes input from user, 
    and if it is valid input, will run command on currently active terminal. 

    Parameters: None
    Returns: None
    """
    stdIn = ""
    while(stdIn != "exit"):
        stdIn = input(Back.BLACK + Back.LIGHTWHITE_EX+Fore.BLACK+'\r').lower().strip()
        if stdIn.startswith("help"):
            if (len(stdIn) == 6 and stdIn[5].isdigit() and 2 >= int(stdIn.split(" ")[1]) > 0):
                ss.update_quadrant(active_terminal, text_dict.get(stdIn))
            else: ss.update_quadrant(active_terminal, text_dict.get('help'))
            ss.print_screen()
        elif stdIn == "game":
            game_input()
            stdIn = ""
            # stdIn = 'term 1'
        elif stdIn == "calc":
            calculate()
        elif stdIn == "bal":
            balance()
        elif stdIn == "list":
            list_properties()
        elif stdIn.startswith("dance"):
            try: 
                for i in range(int(stdIn[6:])):
                    for j in range(4):
                        set_terminal(j+1)
                        sleep(0.05)
            except:
                ss.overwrite(Style.RESET_ALL + Fore.RED + "Something went wrong.")
        elif stdIn.startswith("term "):
            if(len(stdIn) == 6 and stdIn[5].isdigit() and 5 > int(stdIn.split(" ")[1]) > 0):
                set_terminal(int(stdIn.strip().split(" ")[1]))
                ss.print_screen()
                ss.overwrite(Style.RESET_ALL + Fore.GREEN + "\nActive terminal set to " + str(active_terminal) + ".")
            else:
                ss.overwrite(Style.RESET_ALL + Fore.RED + "Include a number between 1 and 4 (inclusive) after 'term' to set the active terminal.")
            pass
        elif stdIn.startswith("deed"):
            if(len(stdIn) > 4):
                ss.update_quadrant(active_terminal, m.deed(stdIn[5:]))
                ss.print_screen()
        elif stdIn == "disable":
            ss.update_quadrant_strictly(active_terminal, m.disable())
            ss.print_screen()
        elif stdIn == "kill":
            ss.update_quadrant_strictly(active_terminal, m.kill())
            ss.print_screen()
        elif stdIn == "exit" or stdIn.isspace() or stdIn == "":
            # On empty input make sure to jump up one console line
            ss.overwrite("\r")
        elif stdIn == "promo":
            import promo
            promo.main()
        else:
            # ss.overwrite('\n' + ' ' * ss.WIDTH)
            ss.overwrite(Style.RESET_ALL + Fore.RED + "Invalid command. Type 'help' for a list of commands.")
    if stdIn == "exit" and game_running:
        ss.overwrite('\n' + ' ' * ss.WIDTH)
        ss.overwrite(Fore.RED + "You are still in a game!")
        get_input()

if __name__ == "__main__":
    """
    Main driver function for player.
    """
    get_graphics()
    initialize()
    # Prints help in quadrant 2 to orient player.
    ss.update_quadrant(2, text_dict.get('help'))
    # ss.update_quadrant(1, text_dict.get('gameboard'))

    ss.print_screen()

    get_input()

    # ss.print_board(text_dict.get('gameboard'))

    # s.print_w_dots("Goodbye!")

def shutdown():
    os.system("shutdown /s /f /t 3 /c \"Terminal Failure: Bankrupt!\"")