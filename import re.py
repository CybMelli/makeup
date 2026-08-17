import re
def password_strength_checker(password):
    Strength = 0
    feedback = []

    if len(password) >= 8:
        Strength += 1
    else:
        feedback.append("at least 8 character")
    if re.search (r"[A-Z]", password):
        Strength += 1
    else:
        feedback.append("at least one uppercase")
    if re.search (r"[a-z]", password):
        Strength += 1
    else:
        feedback.append("at least one lowercase")
    if re.search (r"[@#$%^]", password):
        Strength +=1
    else:
        feedback.append("at least one special character")
    if re.search (r"\d", password):
        Strength +=1
    else:
        feedback.append("at least one number")
    if Strength == 5:
        return("Strong password")
    else:
        return"Weak password"+"".join(feedback)
    
password = input("Enter your passowrd:")
result = password_strength_checker(password)
print(result)