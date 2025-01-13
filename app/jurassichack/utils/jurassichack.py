import random

def question_1(character, check=None, get_answer=False):
    # Quesiton 1

    # seed random using human slug
    random.seed(str(character.name))

    # Create a list of 10000 random numbers between 1000000 and 9999999
    random_numbers = []
    for i in range(10000):
        random_numbers.append(random.randint(100, 999))

    
    # Add all numbers in random_numbers
    total = 0
    for number in random_numbers:
        total += number

    if check:   
        if check == total:
            return True
    
    if get_answer:
        return total
        
    # format random_numbers into a string. Put each number on a new line.
    random_numbers_string = ""
    for number in random_numbers:
        random_numbers_string += f"{number}\n"
    
    return random_numbers_string

def question_2(character, check=None, get_answer=False):
    # Quesiton 2

    # seed random using human slug
    random.seed(str(character.name))

    # Create a list of 10000 random numbers between 1000000 and 9999999
    random_numbers = []
    for i in range(10000):
        random_numbers.append(random.randint(1000, 1999))

    
    # Add all numbers in random_numbers
    total = 0
    for number in random_numbers:
        total += number

    if check:   
        if check == total:
            return True
    
    if get_answer:
        return total
        
    # format random_numbers into a string. Put each number on a new line.
    random_numbers_string = ""
    for number in random_numbers:
        random_numbers_string += f"{number}\n"
    
    return random_numbers_string

def question_3(character, check=None, get_answer=False):
    # Quesiton 3

    # seed random using human slug
    random.seed(str(character.name))

    # Create a list of 10000 random numbers between 1000000 and 9999999
    random_numbers = []
    for i in range(10000):
        random_numbers.append(random.randint(2000, 2999))

    
    # Add all numbers in random_numbers
    total = 0
    for number in random_numbers:
        total += number

    if check:   
        if check == total:
            return True
    
    if get_answer:
        return total
        
    # format random_numbers into a string. Put each number on a new line.
    random_numbers_string = ""
    for number in random_numbers:
        random_numbers_string += f"{number}\n"
    
    return random_numbers_string