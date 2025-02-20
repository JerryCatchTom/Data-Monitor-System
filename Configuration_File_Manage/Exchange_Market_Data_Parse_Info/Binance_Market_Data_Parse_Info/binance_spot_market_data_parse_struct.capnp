@0xab599f19db495710;
struct TickTrade {
                           eventType @0 :Text;        # eg: "trade"
                           timestamp @1 :Int64;  # the occur timestamp of event
                           symbol @2 :Text;           # eg: "BNBBTC"
                           tickTradeId @3 :Int64;# ID
                           tradingPrice @4 :Text;            # string to higher precise
                           tradingVolume @5 :Text;    # string to higher precise
                           tradingTime @6 :Int64;       # traded
                           isMaker @7 :Bool;          # if the Buyer is the maker,if true means the buyer provides liquidity;
                           ignoreField @8 :Bool;     # ignore this field
                        }

struct AggregateTrade {
                           eventType @0 :Text;        # eg: "aggTrade"
                           timestamp @1 :Int64;  # the occur timestamp of event
                           symbol @2 :Text;           # eg: "BNBBTC"
                           aggregateTradeId @3 :Int64;# ID
                           tradingPrice @4 :Text;            # string to higher precise
                           tradingVolume @5 :Text;    # string to higher precise
                           firstTradeId @6 :Int64;    # the first order id being aggregated
                           lastTradeId @7 :Int64;     # the first order id being aggregated
                           tradingTime @8 :Int64;       # traded
                           isMaker @9 :Bool;          # if the Buyer is the maker,if true means the buyer provides liquidity;
                           ignoreField @10 :Bool;     # ignore this field
                        }


struct OrderMarketDepth {
                           lastUpdateId @0 :Text;
                           bids @1 :List(Text);
                           asks @2 :List(Text);

                        }


struct UpdateOrderMarketDepth {
                           eventType @0 :Text;
                           timestamp @1 :Int64;
                           symbol @2 :Text;
                           firstUpdateId @3 :Text;
                           lastUpdateId @4: Text;
                           bids @5: List(Text);
                           asks @6: List(Text);
                        }

struct BestOrder {
                           updateId @0 :Text;        # eg: "trade"
                           symbol @1 :Text;           # eg: "BNBBTC"
                           bidBestPrice @2 :Text;
                           bidBestOrderVolume @3 :Text;
                           askBestPrice @4 :Text;
                           askBestOrderVolume @5 :Text;
                        }




