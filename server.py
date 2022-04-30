import socket
import chatlib
import random
import select

# GLOBALS
users = {}
questions = {}
logged_users = {}
messages_to_send = []  #includes (sock, message_to_send)

SERVER_PORT = 2935
SERVER_IP = "127.0.0.1"
AMOUNT_OF_QUESTIONS = 3


def build_and_send_message(conn, code, msg):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), msg (str)
    Returns: Nothing
    """
    full_msg = chatlib.build_message(code, msg)
    print(full_msg)
    print("[THE SERVER'S MESSAGE] ", full_msg)  # Debug print

    if full_msg != chatlib.ERROR_RETURN:
        messages_to_send.append((conn, full_msg))


def recv_message_and_parse(client_socket):
    """
    Receives a new message from given socket.
    Prints debug info, then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occurred, will return None, None
    """
    data = client_socket.recv(10021).decode()

    if data == "":
        cmd, msg = "", ""

    else:
        cmd, msg = chatlib.parse_message(data)
        print("[THE CLIENT'S MESSAGE IS:] ", (cmd, msg))  # Debug print

        if cmd != chatlib.ERROR_RETURN or msg != chatlib.ERROR_RETURN:
            print("The data is: ", data)
            print("The command: ", cmd)
            print("The message: ", msg)
            print()

    return cmd, msg


def print_client_sockets(list_of_clients):
    counter = 1
    for sock in list_of_clients:
        print("Socket number ", counter, ":", sock.getpeername())
        counter += 1

# Data Loaders #


def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Returns: questions dictionary
    """
    global questions

    questions = open("questions.txt").read().split("\n")
    final_questions = {}

    counter = 1

    for question in questions:
        fildes = {}
        arr = question.split('|')
        if len(arr) == 6:
            question1 = arr[0]
            answers = [arr[1], arr[2], arr[3], arr[4]]
            correct = int(arr[5])
            fildes["question"] = question1
            questions = arr[3]
            fildes["answers"] = answers
            fildes["correct"] = correct

            question_id = counter
            counter += 1

            final_questions[question_id] = fildes

    return final_questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Returns: user dictionary
    """
    global users
    global questions

    users = open("users.txt").read().split("\n")
    final_users = {}

    for user in users:
        fildes = {}
        arr = user.split('|')
        if len(arr) == 4:
            username = arr[0]
            fildes["password"] = arr[1]
            fildes["score"] = int(arr[2])
            questions = arr[3]
            if len(questions) == 0:
                questions_asked = []
            else:
                questions_asked = questions.split(',')
            fildes["questions_asked"] = questions_asked
            final_users[username] = fildes

    return final_users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Returns: the socket object
    """
    server_socket = socket.socket()
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()
    print("Server is up and running")
    return server_socket


def send_error(conn, error_msg):
    """
    Send error message with given message
    Receives: socket, message error string from called function
    Returns: None
    """
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER['login_failed_msg'], error_msg)


#MESSAGE HANDLING

def handle_getscore_message(conn):
    #Sending the client it's score
    score = logged_users[conn.getpeername()]['score']
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER['your_score_msg'], str(score))


def handle_logout_message(conn):
    """
    Closes the given socket (in later chapters, also remove user from logged_users dictionary)
    Receives: socket
    Returns: None
    """
    global logged_users

    if conn.getpeername() in logged_users.keys():
        del logged_users[conn.getpeername()]

    conn.close()


def MAKE_data_id_questions_answers():
    #Returns all the information needed for building a random question.
    global questions
    questions_data = load_questions()
    questions_id = questions_data.keys()

    dict_of_questions = {}  #a dictionary of questions
    dict_of_answers = {}  #a dictionary of answers
    dict_of_correct = {}  #a dictionary of the place of the correct answers

    for id_number in questions_id:
        dict_of_questions[id_number] = questions_data[id_number]["question"]
        dict_of_answers[id_number] = questions_data[id_number]["answers"]
        dict_of_correct[id_number] = questions_data[id_number]["correct"]

    return questions_data, questions_id, dict_of_questions, dict_of_answers, dict_of_correct


def ThePeerNameOfTheUser(User_Name):
    #Returning the peer_name of the user, based on his user_name.
    for peer_name in logged_users.keys():
        if logged_users[peer_name]['user_name'] == User_Name:
            return peer_name


def create_random_question(USER_NAME):
    #Creating a random question.
    questions_data, questions_id, question_dict, answers_dict, correct_dict = MAKE_data_id_questions_answers()

    peer_user = ThePeerNameOfTheUser(USER_NAME)
    questions_already_asked = logged_users[peer_user]['questions_already_asked']

    if len(questions_already_asked) == AMOUNT_OF_QUESTIONS:  #2 is the amount of questions
        return None

    else:
        questions_id = list(questions_id)
        random_id = random.choice(questions_id)
        random_question = question_dict[random_id]

        while random_question in questions_already_asked:
            print("The questions was already asked!")
            questions_id = list(questions_id)
            random_id = random.choice(questions_id)
            random_question = question_dict[random_id]

        ALL_INFO = str(random_id) + "#" + random_question

        for answer in answers_dict[random_id]:
            ALL_INFO += "#" + answer

    return ALL_INFO


def handle_question_message(sock, USERNAME):
    #Handaling a question message.
    message_info = create_random_question(USERNAME)

    if message_info is None:
        build_and_send_message(sock, chatlib.PROTOCOL_SERVER['no_questions_msg'], "")

    else:
        build_and_send_message(sock, chatlib.PROTOCOL_SERVER['your_question_msg'], message_info)

    questions_already_asked = logged_users[sock.getpeername()]['questions_already_asked']

    if len(questions_already_asked) != AMOUNT_OF_QUESTIONS:
        return message_info.split("#")[1]


def handle_answer_message(sock, answer_message):
    #Handaling an answer message
    global questions
    questions = load_questions()

    message = answer_message
    print("The answer is: ", message)

    question_id = int(message.split("#")[0])
    choice = int(message.split("#")[1])

    #if the username wasn't asked this question -> send error
    data_of_question_asked = questions[question_id]
    right_answer = data_of_question_asked["correct"]
    print("The right answer is: ", right_answer)

    if right_answer == choice:  #Send correct_answer message to the client
        print("Your answer is correct! ")
        logged_users[sock.getpeername()]['score'] += 5  #adding 5 to the score of the player
        build_and_send_message(sock, chatlib.PROTOCOL_SERVER['correct_answer_msg'], "")

    else:  #Send wrong_answer message to the client
        print("Your answer is incorrect! ")
        build_and_send_message(sock, chatlib.PROTOCOL_SERVER['wrong_answer_msg'], str(right_answer))


#handles get highscore message
def handle_get_highscore(conn):
    global logged_users

    users_scores = {}
    for peer_name in logged_users.keys():
        key = logged_users[peer_name]['user_name']
        score = logged_users[peer_name]['score']
        users_scores[key] = score

    users_sorted_scores = sorted(users_scores.items(), key=lambda x: x[1], reverse=True)
    users_sorted_scores = users_sorted_scores[:5]

    msg = ""
    for tup in users_sorted_scores:
        msg += tup[0] + ":" + str(tup[1]) + "\n"

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["all_score_msg"], msg)


def IsMatch(User_Name, Password):
    """
    Gets a username and a password.
    Returns if a client with this username and password is connected to the system.
    """
    check = True
    global users
    users = load_user_database()

    if User_Name not in users.keys():
        check = False

    else:
        The_Users_Key = ""
        for key in users.keys():
            if key == User_Name:
                The_Users_Key = key

        if users[The_Users_Key]['password'] != Password:
            check = False

    return check


def IsNameIsLogged(USER_NAME):
    #Prints whether this username is taken or not
    check = False
    for peer_name in logged_users.keys():
        if logged_users[peer_name]['user_name'] == USER_NAME:
            check = True
    return check


#handles logged message
def handle_logged(conn):
    global logged_users

    msg = ""
    for peer_name in logged_users.keys():
        user_name = logged_users[peer_name]['user_name']
        msg = msg + user_name + ","

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_answer_msg"], msg)


def handle_login_message(conn, cmd, message):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Receives: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users' dictionary from all functions
    global logged_users	 # To be used later
    # command, message = recv_message_and_parse(conn)

    if cmd != chatlib.PROTOCOL_CLIENT['login_msg']:
        print("ERROR! The command is not LOGIN!")

    else:
        MESSAGE_AFTER_SPLIT = message.split("#")
        print(MESSAGE_AFTER_SPLIT)
        USER_NAME = MESSAGE_AFTER_SPLIT[0]
        PASSWORD = MESSAGE_AFTER_SPLIT[1]

        if not IsMatch(USER_NAME, PASSWORD):
            print("ERROR! The password doesn't match to the username!")
            send_error(conn, "Doesnt match")

        else:
            if IsNameIsLogged(USER_NAME):
                print("ERROR! The password doesn't match to the username!")
                send_error(conn, "Doesnt match")

            else:
                print("Sending to the client LOGIN_OK...")
                build_and_send_message(conn, chatlib.PROTOCOL_SERVER['login_ok_msg'], "")

                #adding to the dictionary
                if conn.getpeername() not in logged_users.keys():
                    logged_users[conn.getpeername()] = {}
                    logged_users[conn.getpeername()]['questions_already_asked'] = []
                    logged_users[conn.getpeername()]['score'] = 0
                    logged_users[conn.getpeername()]['user_name'] = USER_NAME


def handle_client_message(conn, cmd, message):
    """
    Gets message code and data and calls the right function to handle command
    Receives: socket, message code and data
    Returns: None
    """
    global logged_users	 # To be used later

    if cmd not in chatlib.PROTOCOL_CLIENT.values():
        send_error(conn, "We are not familiar with the command!")

    else:
        if cmd == chatlib.PROTOCOL_CLIENT['login_msg']:
            handle_login_message(conn, cmd, message)

        elif cmd == chatlib.PROTOCOL_CLIENT['logged_msg']:
            handle_logged(conn)

        elif cmd == chatlib.PROTOCOL_CLIENT['get_question_msg']:
            USER_NAME = logged_users[conn.getpeername()]['user_name']
            question = handle_question_message(conn, USER_NAME)
            questions_already_asked = logged_users[conn.getpeername()]['questions_already_asked']

            if len(logged_users[conn.getpeername()]['questions_already_asked']) != AMOUNT_OF_QUESTIONS:
                questions_already_asked.append(question)

            print("Already asked: ", questions_already_asked)

        elif cmd == chatlib.PROTOCOL_CLIENT['send_answer_msg']:
            if len(logged_users[conn.getpeername()]['questions_already_asked']) != AMOUNT_OF_QUESTIONS + 1:
                handle_answer_message(conn, message)
            else:
                print("GAME OVER!")

        elif cmd == chatlib.PROTOCOL_CLIENT['my_score_msg']:
            handle_getscore_message(conn)

        elif cmd == chatlib.PROTOCOL_CLIENT['high_score_msg']:
            handle_get_highscore(conn)


def main():
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions
    global messages_to_send

    print("Welcome to Trivia Server!")
    server_socket = setup_socket()

    print("Listening for clients... ")
    client_sockets = []

    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets, [])

        for current_socket in ready_to_read:
            if current_socket is server_socket:
                (client_socket, client_address) = server_socket.accept()
                print(f"new client connected: {client_address}")
                client_sockets.append(client_socket)

            else:
                print("New data from client!")
                cmd, msg = recv_message_and_parse(current_socket)
                if cmd == "" and msg == "" or cmd == chatlib.PROTOCOL_CLIENT['logout_msg']:
                    del (logged_users[tuple(current_socket.getpeername())])
                    ready_to_write.remove(current_socket)
                    client_sockets.remove(current_socket)
                    current_socket.close()

                else:
                    handle_client_message(current_socket, cmd, msg)

            print_client_sockets(client_sockets)
            print(logged_users)

        for message in messages_to_send:
            current_socket, data = message
            current_socket.send(data.encode())
            messages_to_send.remove(message)


if __name__ == '__main__':
    main()
