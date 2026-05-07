# app/services/suggestion_engine.py

def calculate_rounding(amount: float):
    last_digit = int(amount) % 10

    if last_digit == 5:
        rounded = amount + 1

    elif last_digit < 5:
        rounded = amount + (5 - last_digit)

    else: 
        rounded = amount + (10 - last_digit)

    spare = rounded - amount

    return {
        "original": amount,
        "rounded": rounded,
        "spare": spare,
        "options": [
            amount,
            amount + 5,
            amount + 10
        ]
    }
 