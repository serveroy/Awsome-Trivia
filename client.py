import socket
import chatlib

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 2935
ListOfDesires = ['m', 'q', 't', 'h', 'l']


def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """
    full_msg = chatlib.build_message(code, msg)
    print("[THE CLIENT'S MESSAGE] ", full_msg)  # Debug print
    conn.send(full_msg.encode())


def recv_message_and_parse(conn):
    """
    Receives a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occurred, will return None, None
    """
    data = conn.recv(10021).decode()
    cmd, msg = chatlib.parse_message(data)
    print("[THE SERVER'S MESSAGE IS:] ", (cmd, msg))  # Debug print

    if cmd != chatlib.ERROR_RETURN or msg != chatlib.ERROR_RETURN:
        print("The data is: ", data)
        print("The command: ", cmd)
        print("The message: ", msg)
        print()

    return cmd, msg


def build_send_recv_parse(conn, code, msg):
    """
    Gets a socket(conn), the command (code) and the message (msg)
    It uses the function build_and_send_message, and recv_message_and_parse.
    """
    build_and_send_message(conn, code, msg)
    cmd, message = recv_message_and_parse(conn)
    return cmd, message


def get_score(conn):
    """
    Gets a socket(conn) and prints the current score of the user.
    """
    cmd, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['my_score_msg'], "")
    print((cmd, msg))

    if cmd != 'YOUR_SCORE':
        return chatlib.ERROR_RETURN

    else:
        return cmd, msg


def play_question(conn):
    """
    Gets a socket(conn)

    """
    cmd, msg = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['get_question_msg'], "")
    print(cmd)

    if cmd == chatlib.PROTOCOL_SERVER['no_questions_msg']:
        print("THERE ARE NO QUESTIONS LEFT!")  #Do I need to send the server something?

    elif cmd == chatlib.PROTOCOL_SERVER['your_question_msg']:
        MSG_AFTER_SPLIT = msg.split("#")  #The details of the question in a list
        ID = MSG_AFTER_SPLIT[0]
        QUESTION = MSG_AFTER_SPLIT[1]
        OPTIONS = MSG_AFTER_SPLIT[2:]

        print("The question: ", QUESTION)
        print("The options for the answer:\n\t")
        for option in OPTIONS:
            print(option, '\n\t')

        ANSWER = str(input("Enter your answer: "))

        while ANSWER not in OPTIONS:
            print("Error! The answer is not in the options!!")
            ANSWER = str(input("Enter your answer: "))

        place = 0
        for i in range(len(OPTIONS)):
            if OPTIONS[i] == ANSWER:
                place = i + 1

        Message = ID + "#" + str(place)
        server_command, message = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['send_answer_msg'], Message)

        if server_command == chatlib.PROTOCOL_SERVER['correct_answer_msg']:
            print("Your answer is correct!")
            print("The message from the server is: ", message)

        if server_command == chatlib.PROTOCOL_SERVER['wrong_answer_msg']:
            print("Your answer is incorrect!")
            print("The message from the server is: ", message)

            right_answer_place = int(message) - 1
            RIGHT_ANSWER = OPTIONS[right_answer_place]

            print("The right answer is: ", RIGHT_ANSWER)


def get_high_score(conn):
    """
    Gets a socket(conn).
    Prints the highscores table as it arrives from the server
    """
    command, message = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['high_score_msg'], "")
    print("The high scores table: \n", message)


def get_logged_users(conn):
    """
    Gets a socket(conn).
    Prints the list of the logged users as it arrives from the server
    """
    command, message = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT['logged_msg'], "")
    print("The logged users: \n", message)


def connect():
    """
    Connects the socket to the server.
    """
    my_socket = socket.socket()
    my_socket.connect((SERVER_IP, SERVER_PORT))
    return my_socket


def error_and_exit(msg):
    exit()


def login(conn):
    """
    Asking of username and password, and creates a new user.
    """
    username = input("Please enter username: \n")
    password = input("Please enter password: \n")
    whole_message = username + "#" + password
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], whole_message)
    data = conn.recv(10024).decode()
    command, message = chatlib.parse_message(data)

    while data == chatlib.ERROR_RETURN or command == chatlib.PROTOCOL_SERVER['login_failed_msg']:
        print("The login failed!")
        username = input("Please enter username: \n")
        password = input("Please enter password: \n")
        whole_message = username + "#" + password
        build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["login_msg"], whole_message)
        data = conn.recv(10024).decode()
        command, message = chatlib.parse_message(data)

    return data


def logout(conn):
    """
    Doing a logout
    """
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")


def main():
    my_socket = connect()
    data = login(my_socket)

    print("The login succeeded!")
    print("The message from the server: ", data)

    print("Your options: \n\t m - Get My Score \n\t q - quit \n\t t - Play a trivia question \n\t h - Get The High Scores \n\t l - Get Logged Users")
    desire = str(input("Enter what do you want to do: "))

    while desire not in ListOfDesires:
        print("Error! Enter again!")
        desire = str(input("Enter what do you want to do: "))

    while desire != 'q':
        if desire == 'm':
            cmd, score = get_score(my_socket)
            print("Your score is: ", int(score))

        elif desire == 't':
            print("Asking the server for a trivia question. ")
            play_question(my_socket)

        elif desire == 'h':
            print("The high scores table: ")
            get_high_score(my_socket)

        elif desire == 'l':
            print("The list of the logged users: ")
            get_logged_users(my_socket)

        print("Your options: \n\t m - Get My Score \n\t q - quit \n\t t - Play a trivia question \n\t h - Get The High Scores \n\t l - Get Logged Users")
        desire = str(input("Enter what do you want to do: "))

        while desire not in ListOfDesires:
            print("Error! Enter again!")
            desire = str(input("Enter what do you want to do: "))

    logout(my_socket)


if __name__ == '__main__':
    main()
