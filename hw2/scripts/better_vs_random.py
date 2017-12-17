import subprocess

better_wins_simple_when_first = 0
better_wins_simple_when_second = 0
better_wins_random_when_first = 0
better_wins_random_when_second = 0

extent = 10
weWantRanAlso = True
for i in range(extent):
    result = subprocess.check_output("python ../run_game.py 2 10 5 n better_player simple_player", shell=True)
    if 'better' in result.decode("utf-8"):
        better_wins_simple_when_first += 1

for i in range(extent):
    result = subprocess.check_output("python ../run_game.py 2 10 5 n simple_player better_player", shell=True)
    if 'better' in result.decode("utf-8"):
        better_wins_simple_when_second += 1
if weWantRanAlso:
    for i in range(extent):
        result = subprocess.check_output("python ../run_game.py 2 10 5 n random_player better_player", shell=True)
        if 'better' in result.decode("utf-8"):
            better_wins_random_when_second += 1
    for i in range(extent):
        result = subprocess.check_output("python ../run_game.py 2 10 5 n better_player random_player", shell=True)
        if 'better' in result.decode("utf-8"):
            better_wins_random_when_first += 1

    print("better won random {0} times when was first".format(better_wins_random_when_first))
    print("better won random {0} times when was second".format(better_wins_random_when_second))

print("better won simple {0} times when was first".format(better_wins_simple_when_first))
print("better won simple {0} times when was second".format(better_wins_simple_when_second))


