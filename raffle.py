class Raffle:
    def __init__(self, max_bet):
        self.max_bet = max_bet
        self.players = dict()
        self.tickets = list()
        self.prize = 0