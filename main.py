# import all of the simulators
from baseball import Baseball
from basketball import Basketball
from football import Football
from hockey import Hockey
from futbol import Futbol

# print something cool
print("\n- - - - - Jensen's Sports Simulator - - - - -")

def sport_error_message(input_):
    print(f'\nERROR: You entered {input_}, which is not a valid input.')
    print(f'Acceptable inputs at this time include: \nBaseball\nFootball\nBasketball\nFutbol\nHockey')

SPORT = input('\nEnter Sport: ')

if SPORT.lower().strip() == 'baseball':
    Baseball()
elif SPORT.lower().strip() == 'basketball':
    Basketball()
elif SPORT.lower().strip() == 'football':
    Football()
elif SPORT.lower().strip() == 'hockey':
    Hockey()
elif SPORT.lower().strip() == 'futbol':
    Futbol()
else:
    sport_error_message(SPORT)