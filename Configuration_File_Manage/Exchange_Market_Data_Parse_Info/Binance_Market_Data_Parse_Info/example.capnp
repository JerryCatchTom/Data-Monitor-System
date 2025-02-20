@0xab599f19db495710;
struct SpotTickTrade {
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

