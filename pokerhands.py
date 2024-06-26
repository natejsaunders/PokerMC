# Poker hand win probability calculator using Monte-Carlo Simulation
# By Nate Saunders
# v0.1 7/9/23

import random

# Class containing all information for the simulation itself
class poker_simulation:

    def __init__(self, hands, community):
        # Generating a deck
        self.suits = ["♣","♦","♠","♥"]
        self.ranks = list("23456789TJQKA")#{"2":2,"3":3,"4":4,"5":5,"6":6,"7":7,"8":8,"9":9,"T":10,"J":11,"Q":12,"K":13,"A":14}
        self.deck = [suit + rank for rank in self.ranks for suit in self.suits]

        # Used for 
        self.hand_rankings = ["High Card", "Pair", "Two Pair","Three of a Kind", "Straight", "Flush", "Full House", "Four of a Kind", "Straight Flush"]

        # Removing cards that have already been drawn
        for hand in hands:
            for card in hand:
                self.deck.remove(card)

        for card in community:
            self.deck.remove(card)

        self.community = community
        self.hands = hands

        # Store winning results to the class (not currently in use)
        self.winners = {}
        for h in self.hands:
            self.winners[str(h)] = 0

    # Returns an array that is used to compare hand rankings
    # What each number in the array means is explained in the check for each ranking
    def find_hand_ranking(self, hand):

        hand.sort(key = self.rank, reverse = True)

        # Count up the number of each rank and suit
        rank_counts = {rank : 0 for rank in self.ranks}
        suit_counts = {suit : 0 for suit in self.suits}

        for card in hand:
            rank_counts[card[1]] += 1
            suit_counts[card[0]] += 1

        # Checking for flush
        flush_suit = ''
        is_flush = False
        for suit, count in suit_counts.items():
            if count >= 5:
                is_flush = True
                flush_suit = suit

        # NEED TO FIX STRAIGH FLUSH THEY CURRENTLY HAPPEN TOO OFTEN
        is_straight_flush = False
        is_straight = False
        straight_rank = 0

        # Adding ace as 1 to help with straights
        rank_counts['1'] = rank_counts['A']
        ranks = list("123456789TJQKA")

        # Check if there are any straights (if there are at least one of any 5 cards in a row based on rank)
        for start in range(len(ranks) - 4):
            if all(rank_counts[ranks[i]] >= 1 for i in range(start, start + 5)):
                is_straight = True
                straight_rank = self.rank(ranks[start + 4])

        # Removing the 1 as it causes issues with two pair
        rank_counts.pop('1')

        if is_flush and is_straight:
            # Straigh Flush 
            # Returns 8 then the highest card in the straight
            # DOESN'T WORK AS WE COUNT 7 CARDS FOR STRAIGHT AND FLUSH NOT 5 AAAAAAAAAAAAAAAAAAAAAAAa

            # Fun to see how often Royal Flushes happen
            #if straight_rank == 14:
            #    print("Royal Flush!!")

            return [8, straight_rank]
        
        if any(count == 4 for count in rank_counts.values()):
            # Four of a Kind
            # Returns 7, then the value of the 4 card then the rank of the next highest card
            
            four_value = 0
            highest_card = 0
            for rank in rank_counts:
                value = self.rank("X" + rank) # bit of a jank i know
                if rank_counts[rank] == 4:
                    four_value = value
                if rank_counts[rank] < 4 and rank_counts[rank] > 0 and value > highest_card:
                    highest_card = value

            return [7, four_value, highest_card]
        
        if 3 in rank_counts.values() and 2 in rank_counts.values():
            # Full House
            # FIXED(THIS DOES NOT CURRENTLY WORK: because we are considering 7 cards total, there could be two three of a kinds that should still be considered a Full House but isn't)
            # Returns 6 then the value of the triple then the value of the pair

            triple_value = 0
            pair_value = 0

            for rank in rank_counts:
                value = self.rank("X" + rank) # bit of a jank i know
                if rank_counts[rank] == 3:
                    triple_value = value
                if rank_counts[rank] == 2:
                    pair_value = value
            
            #print(hand)
            #print([6, triple_value, pair_value])
            return [6, triple_value, pair_value]
        
        if list(rank_counts.values()).count(3) == 2:
            # ALSO FULL HOUSE

            triple_value = 0
            pair_value = 0

            for rank in rank_counts:
                value = self.rank("X" + rank) # bit of a jank i know
                if rank_counts[rank] == 3 and value > triple_value:
                    pair_value = triple_value
                    triple_value = value
                elif rank_counts[rank] == 3:
                    pair_value = value

            #print(hand)
            #print([6, triple_value, pair_value])
            return [6, triple_value, pair_value]
        
        if is_flush:
            # Flush
            # Returns 5 then the highest card in the flush

            flush_high = 0
            for card in hand:
                if card[0] == flush_suit:
                    flush_high = self.rank(card)

            return [5, flush_high]
        
        if is_straight:
            # Straight
            # Returns 4 then the highest card in the straight

            return [4, straight_rank]
        
        if any(count == 3 for count in rank_counts.values()):
            # Three of a Kind
            # Returns 3 then the value of the triple, then the value of the next two high cards (we can assume they are not a pair as this should have been covered by Full House)

            triple_value = 0
            for rank in rank_counts:
                if rank_counts[rank] == 3:
                    triple_value = self.rank("X" + rank) # bit of a jank i know

            highest_cards = []
            for card in hand:
                value = self.rank(card[1])
                if rank_counts[card[1]] < 2 and len(highest_cards) < 2:
                    highest_cards.append(value)

            return [3, triple_value] + highest_cards
        
        if list(rank_counts.values()).count(2) == 2:
            # Two Pair 
            # Returns 2 then the value of the highest and lower pair then the value of the high card

            high_pair_value = 0
            low_pair_value = 0
            for rank in rank_counts:
                value = self.rank("X" + rank) # bit of a jank i know
                if rank_counts[rank] == 2 and value > high_pair_value:
                    high_pair_value = value
            for rank in rank_counts:
                value = self.rank("X" + rank) # bit of a jank i know
                if rank_counts[rank] == 2 and value > low_pair_value and value != high_pair_value:
                    low_pair_value = value

            highest_card = 0
            for card in hand:
                value = self.rank(card[1])
                if rank_counts[card[1]] < 2 and value > highest_card:
                    highest_card = value

            return [2, high_pair_value, low_pair_value, highest_card]
        
        if any(count == 2 for count in rank_counts.values()):
            # Pair
            # Returns 1 then the value of the pair then the value of the next 3 high cards

            pair_value = 0
            for rank in rank_counts:
                if rank_counts[rank] == 2:
                    pair_value = self.rank("X" + rank)

            highest_cards = []
            for card in hand:
                value = self.rank(card[1])
                if rank_counts[card[1]] < 2 and len(highest_cards) < 3:
                    highest_cards.append(value)

            return [1, pair_value] + highest_cards
        
        # High Card
        # Return 0 then the rankings of the top 5 cards in the hand

        highest_cards = []
        for card in hand:
            value = self.rank(card[1])
            if rank_counts[card[1]] < 2 and len(highest_cards) < 5:
                highest_cards.append(value)

        return [0] + highest_cards

    # Compares hand rankings and returns the higher, see above how hand rankings are calculated
    def compare_hands(self, hand_A, hand_B):

        hand_a = hand_A + self.community
        hand_b = hand_B + self.community

        hand_a_ranking = self.find_hand_ranking(hand_a)
        hand_b_ranking = self.find_hand_ranking(hand_b)

        for i in range(min(len(hand_a_ranking), len(hand_b_ranking))):
            if hand_a_ranking[i] > hand_b_ranking[i]:
                return hand_A
            elif hand_a_ranking[i] < hand_b_ranking[i]:
                return hand_B
    
        if hand_a_ranking == hand_b_ranking:
            return 'tie'
        
        error_msg = "No best hand selected." + str(hand_a_ranking) + str(hand_a) + str(hand_b_ranking) + str(hand_b)
        raise Exception(error_msg)

    # Return the integer rank of the card input
    def rank(self, card):
        return self.ranks.index(card[-1]) + 2

    # Run a single round of poker, draw all cards then output any winners and whether there is a tie
    def run(self):

        # Shuffle deck
        random.shuffle(self.deck)

        # Draw other players cards
        for i in range(len(self.hands)):
            while len(self.hands[i]) < 2:
                self.hands[i].append(self.deck.pop())

        # Draw remaining community cards
        while len(self.community) < 5:
            self.community.append(self.deck.pop()) 

        best_hands = [self.hands[0]]
        tie = False

        # Compare hands to find winner
        for i in range(1, len(self.hands)):
            hand = self.hands[i]

            compare = self.compare_hands(best_hands[0], hand)
            if compare == 'tie':
                tie = True
                best_hands.append(hand)
            else:
                best_hands = [compare]
                tie = False

        return tie, best_hands

# Change these \/\/\/
simulations = 100000
player_hands = [['♠6', '♠7'],
                ['♦A', '♣9'],
                ['♣A', '♣K'],
                ['♦T', '♦J'],
                ['♣2', '♠4'],
                ]

# The winners are stored in a dict: the key is the hand, index 0 is wins and 1 is ties
winners = {}
for h in player_hands:
    winners[str(h)] = [0,0]


percent_complete = 0
for i in range(simulations):

    ps = poker_simulation(player_hands, ['♣Q','♣J','♣T'])

    tie, sim_winners = ps.run()
    
    # If there is a tie, an array of winners get +1 ties, otherwise the singular winner will get +1 wins (stored at index 1 and 0 respectivley)
    if tie: 
        for w in sim_winners:
            winners[str(w)][1] += 1
    else:    winners[str(sim_winners[0])][0] += 1

    # Loading bar
    if i % (simulations // 100) == 0:
        percent_complete += 1
        loading_bar_start = ["█" for ii in range(i // (simulations // 30))]
        loading_bar = loading_bar_start + [" " for ii in range(30 - i // (simulations // 30))]
        print("[", "".join(loading_bar), "]  ", percent_complete, "%", end = "\r", sep="")

print("\r\n")

# Output results
for hand, data in winners.items():
    print(hand, "wins", round(data[0] / simulations * 100, 1), "% of the time and ties", round(data[1] / simulations * 100, 1), "% of the time.")

print("\nFor", simulations, "simulations.")