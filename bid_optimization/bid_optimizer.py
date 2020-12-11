#!/usr/bin/env python3


class BidOptimizer:
    def __init__(self, caller, cost_function):
        self.caller = caller
        self.cost_function = cost_function
        self.participating_auctions = {}
        self.on_going_auctions = {}
        self.utilities = {}
        pass

    def utility_function(self, auction):
        return auction.get_current_pay() - self.cost_function(
            auction, self.participating_auctions)

    def evaluate_and_bid(self, recompute_utilities=False):
        best_auctions = [None, None]
        won_auctions = []
        for auction_id, auction in list(self.on_going_auctions.items()):
            if auction_id in self.participating_auctions:
                if auction.get_contractor() == self.caller:
                    continue
                else:
                    del self.participating_auctions[auction_id]
            # delete expired auctions
            if not auction.accepting_bids():
                # check if you won the auction
                if auction.get_contractor() == self.caller:
                    won_auctions.append(auction)
                del self.on_going_auctions[auction_id]
                del self.utilities[auction_id]
                continue
            if recompute_utilities:
                self.utilities[auction_id] = self.utility_function(auction)
            # reject negative utilities
            if self.utilities[auction_id] <= 0:
                continue
            # find the highest utility auctions
            if best_auctions[0] is None or self.utilities[
                    auction_id] > self.utilities[best_auctions[0]]:
                best_auctions[0] = auction_id
            elif best_auctions[1] is None or self.utilities[
                    auction_id] > self.utilities[best_auctions[1]]:
                best_auctions[1] = auction_id
        # bid on the best auction at a price of decision boundary between second best
        if best_auctions[0] is not None:
            best_auction = self.on_going_auctions[best_auctions[0]]
            # TODO handle bidding errors
            bid_price = min(
                best_auction.get_current_bid() * 99 // 100,
                max(
                    best_auction.get_current_bid() // 2,
                    best_auction.get_current_pay() -
                    self.utilities[best_auctions[0]] +
                    0 if best_auctions[1] is None else
                    self.utilities[best_auctions[1]]))
            best_auction.bid(self.caller, bid_price)
            self.participating_auctions[best_auctions[0]] = best_auction
        return best_auctions[0], won_auctions

    def on_auction_update(self, auction_id, auction):
        '''possible events: creation, bid, cancel,    extend, confirm'''
        # check if participating auction was out bid
        if auction_id in self.participating_auctions and auction.get_contractor(
        ) != self.caller:
            del self.participating_auctions[auction_id]
        # update utility only if bid was updated
        if auction_id not in self.on_going_auctions or auction.get_current_bid(
        ) != self.on_going_auctions[auction_id].get_current_bid():
            self.utilities[auction_id] = self.utility_function(auction)
        # store updated auction
        self.on_going_auctions[auction_id] = auction
