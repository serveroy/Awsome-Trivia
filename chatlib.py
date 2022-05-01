# Protocol Constants
CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol

# Protocol Messages
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "logged_msg": "LOGGED",
    "get_question_msg": "GET_QUESTION",
    "send_answer_msg": "SEND_ANSWER",
    "my_score_msg": "MY_SCORE",
    "high_score_msg": "HIGHSCORE"
}

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "logged_answer_msg": "LOGGED_ANSWER",
    "your_question_msg": "YOUR_QUESTION",
    "correct_answer_msg": "CORRECT_ANSWER",
    "wrong_answer_msg": "WRONG_ANSWER",
    "your_score_msg": "YOUR_SCORE",
    "all_score_msg": "ALL_SCORE",
    "login_failed_msg": "ERROR",
    "no_questions_msg": "NO_QUESTIONS"
}

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message_with_correct_inputs(cmd, data):
    """
    Gets valid command name and data field according to the protocol.
    Returns: str
    """

    full_msg = ""

    ORDER_PART = ""  # length - 16, the order - cmd.
    L_PART = ""  # length - 4, declares the length of the M_PART.
    M_PART = ""  # The message - data.

    # Building each part:
    ORDER_PART += cmd  # The cmd part
    while len(ORDER_PART) < CMD_FIELD_LENGTH:
        ORDER_PART += " "

    for i in range(LENGTH_FIELD_LENGTH - len(str(len(data)))):  # The length part
        L_PART += "0"
    L_PART += str(len(data))

    if data == "":
        full_msg = full_msg + ORDER_PART + DELIMITER + L_PART + DELIMITER

    else:
        M_PART += data
        full_msg = full_msg + ORDER_PART + DELIMITER + L_PART + DELIMITER + M_PART

    return full_msg


def Handle_Client_Message(cmd, data):
    full_msg = ""
    if cmd != PROTOCOL_CLIENT['login_msg'] and cmd != PROTOCOL_CLIENT['send_answer_msg']:  # The data needs to be empty in that case
        if data != "":
            full_msg = ERROR_RETURN

        else:
            full_msg = build_message_with_correct_inputs(cmd, data)

    else:  # The data needs to not be empty in that case
        if data == "":
            full_msg = build_message_with_correct_inputs(cmd, data)

        else:
            if cmd == PROTOCOL_CLIENT['login_msg']:
                PARTS_OF_LOGIN = data.split("#")
                if len(PARTS_OF_LOGIN) >= 2:
                    full_msg = build_message_with_correct_inputs(cmd, data)
                else:
                    full_msg = ERROR_RETURN

            if cmd == PROTOCOL_CLIENT['send_answer_msg']:
                PARTS_OF_SEND_ANSWER = data.split("#")
                if len(PARTS_OF_SEND_ANSWER) == 2:
                    part_1 = PARTS_OF_SEND_ANSWER[0]
                    part_2 = PARTS_OF_SEND_ANSWER[1]

                    if type(part_1) == str and type(part_2) == str:
                        if part_1.isdigit() and part_2.isdigit():
                            if 1 <= int(part_2) <= 4:
                                full_msg = build_message_with_correct_inputs(cmd, data)
                            else:
                                full_msg = ERROR_RETURN
                        else:
                            full_msg = ERROR_RETURN
                    else:
                        full_msg = ERROR_RETURN
                else:
                    full_msg = ERROR_RETURN

    return full_msg


def IsItAllString(data_list):
    check = True
    for item in data_list:
        if type(item) != str:
            check = False
    return check


def Handle_Server_Message(cmd, data):
    full_msg = ""
    if cmd != PROTOCOL_SERVER['logged_answer_msg'] and cmd != PROTOCOL_SERVER['your_question_msg'] and cmd != PROTOCOL_SERVER['wrong_answer_msg'] and cmd != PROTOCOL_SERVER['your_score_msg'] and cmd != PROTOCOL_SERVER['all_score_msg'] and cmd != PROTOCOL_SERVER['login_failed_msg']:
        if data != "":
            full_msg = ERROR_RETURN
        else:
            full_msg = build_message_with_correct_inputs(cmd, data)
    else:
        if data == "" and cmd != PROTOCOL_SERVER['login_failed_msg']:
            full_msg = ERROR_RETURN

        else:
            if cmd == PROTOCOL_SERVER['logged_answer_msg']:
                DATA_AFTER_SPLIT = data.split(",")
                if IsItAllString(DATA_AFTER_SPLIT) is False:
                    full_msg = ERROR_RETURN
                else:
                    full_msg = build_message_with_correct_inputs(cmd, data)

            if cmd == PROTOCOL_SERVER['your_question_msg']:
                DATA_AFTER_SPLIT = data.split("#")
                if len(DATA_AFTER_SPLIT) != 6 or IsItAllString(DATA_AFTER_SPLIT) is False or DATA_AFTER_SPLIT[0].isdigit() is False:
                    full_msg = ERROR_RETURN
                else:
                    full_msg = build_message_with_correct_inputs(cmd, data)

            if cmd == PROTOCOL_SERVER['wrong_answer_msg']:
                if data.isdigit() is False:
                    full_msg = ERROR_RETURN
                else:
                    if 1 <= int(data) <= 4:
                        full_msg = build_message_with_correct_inputs(cmd, data)
                    else:
                        full_msg = ERROR_RETURN

            if cmd == PROTOCOL_SERVER['your_score_msg']:
                if data.isdigit() is False:
                    full_msg = ERROR_RETURN
                else:
                    full_msg = build_message_with_correct_inputs(cmd, data)

            if cmd == PROTOCOL_SERVER['all_score_msg']:
                DATA_AFTER_SPLIT = data.split("\n")

                for i in range(len(DATA_AFTER_SPLIT)):
                    if DATA_AFTER_SPLIT[i] == "":
                        DATA_AFTER_SPLIT = DATA_AFTER_SPLIT.pop(i)

                if len(DATA_AFTER_SPLIT) > 5:
                    full_msg = ERROR_RETURN

                else:
                    count = 0
                    for item in DATA_AFTER_SPLIT:
                        ITEM_AFTER_SPLIT = item.split(":")

                        if len(ITEM_AFTER_SPLIT) == 2 or ITEM_AFTER_SPLIT[1].isdigit() is True:
                            count += 1

                    if count == len(DATA_AFTER_SPLIT):
                        full_msg = build_message_with_correct_inputs(cmd, data)

                    else:
                        full_msg = ERROR_RETURN

            if cmd == PROTOCOL_SERVER['login_failed_msg']:
                full_msg = build_message_with_correct_inputs(cmd, data)

    return full_msg


def build_message(cmd, data):
    """
    Gets command name and data field and creates a valid protocol message
    Returns: str, or None if error occurred.
    """
    if (cmd not in PROTOCOL_CLIENT.values() and cmd not in PROTOCOL_SERVER.values()) or len(cmd) > 16 or type(data) != str:
        full_msg = ERROR_RETURN

    else:
        if cmd in PROTOCOL_CLIENT.values():
            full_msg = Handle_Client_Message(cmd, data)

        else:
            full_msg = Handle_Server_Message(cmd, data)

    return full_msg


def IsThereMakaf(my_string):
    check = False
    for i in range(len(my_string)):
        if my_string[i] == "-":
            check = True
    return check


def IsThere_Numbers(my_string):
    check = False
    for i in range(len(my_string)):
        if my_string[i].isdigit() and my_string[i] != "0":
            check = True
    return check


def find_the_number(my_string):
    new_string = ""
    if IsThere_Numbers(my_string) is False:
        return True, 0

    # First handaling
    for i in range(len(my_string)):
        item = my_string[i]

        if item.isdigit():
            if item == "0" and i != len(my_string) - 1:
                if not (my_string[i + 1].isdigit() or my_string[i + 1] == '-' or my_string[i + 1] == '\t' or my_string[i + 1] == '\r'):
                    return False, ERROR_RETURN

                elif IsThere_Numbers(new_string):
                    new_string += item

            else:
                new_string += item

        if item == '-' and i != len(my_string) - 1:
            if my_string[i + 1].isdigit() and my_string[i + 1] != '0' and IsThereMakaf(new_string) is False:
                new_string += item

    if not IsThere_Numbers(new_string):
        return False, ERROR_RETURN

    return True, int(new_string)


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occurred, returns None, None
    """

    # The function should return 2 values

    # checking if the data is valid according to the protocol
    DATA_AFTER_SPLIT = data.split(DELIMITER)
    # print("The list: ", DATA_AFTER_SPLIT)

    if len(DATA_AFTER_SPLIT) != 2 and len(DATA_AFTER_SPLIT) != 3:
        return ERROR_RETURN, ERROR_RETURN

    else:
        # Checking the cmd part
        ORDER_PART = DATA_AFTER_SPLIT[0]

        if len(ORDER_PART) != CMD_FIELD_LENGTH:
            return ERROR_RETURN, ERROR_RETURN

        else:
            ORDER_PART_AFTER_SPLIT = ORDER_PART.split(" ")

            # finding the non-empty part in order_part_after_split
            NON_EMPTY_LIST = []
            for item in ORDER_PART_AFTER_SPLIT:
                if item != "":
                    NON_EMPTY_LIST.append(item)

            if len(NON_EMPTY_LIST) != 1:
                return ERROR_RETURN, ERROR_RETURN

            else:
                if NON_EMPTY_LIST[0] in PROTOCOL_SERVER.values() or NON_EMPTY_LIST[0] in PROTOCOL_CLIENT.values():
                    cmd = NON_EMPTY_LIST[0]
                    # print("The command: ", cmd)

                else:
                    return ERROR_RETURN, ERROR_RETURN

                # checking the L part
                L_PART = DATA_AFTER_SPLIT[1]

                if len(L_PART) != LENGTH_FIELD_LENGTH:
                    return ERROR_RETURN, ERROR_RETURN

                else:
                    check, NUMBER = find_the_number(L_PART)
                    # print("The number of the length part: ", NUMBER)

                    if check is False or NUMBER < 0 or NUMBER > 9999:
                        return ERROR_RETURN, ERROR_RETURN

                    else:
                        # checking the M part
                        M_PART = DATA_AFTER_SPLIT[2]
                        # print("The message part: ", M_PART)

                        if NUMBER != len(M_PART):
                            return ERROR_RETURN, ERROR_RETURN

                        else:
                            msg = M_PART

    return cmd, msg
