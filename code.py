import random

last_code = ""

def create_validation_code():
    global last_code, execution_done
    digit1 = random.randint(0,9)
    digit2 = random.randint(0,9)
    digit3 = random.randint(0,9)
    digit4 = random.randint(0,9)
    final_code = '{}{}{}{}'.format(digit1, digit2, digit3, digit4)
    last_code = final_code
    return final_code

def get_last_code():   
    return last_code  

def reset_code():
    global last_code
    last_code = "" 
    return    