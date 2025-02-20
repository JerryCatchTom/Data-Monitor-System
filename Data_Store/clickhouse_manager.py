import clickhouse_connect
from clickhouse_driver import Client
from global_manager import Global_Variable_Manager
global_variable_manager = Global_Variable_Manager()

from base_database_manager import Base_Database_Manager

class Clickhouse_Manager(Base_Database_Manager):
    def __init__(self,client:Client=None):
        self.__config_info_file_path = ""
        self.config_info = Base_Database_Manager.database_config_info["clickhouse_config_info"]
        print(self.config_info)
        if client:
            self.client = client
        else:
            clickhouse_client = global_variable_manager.get("clickhouse_client")
            if clickhouse_client:
                self.client = clickhouse_client
            else:
                self.client = Client(host=self.config_info["database"]["host"],
                                     port=self.config_info["database"]["port"],
                                     user=self.config_info["database"]["user"],
                                     password=self.config_info["database"]["password"],
                                     database=self.config_info["database"]["database"])
                self.client.execute('SELECT version()')

    def execute(self, *args, **kwargs):
        pass

def create_exchange_info_table():
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    version = client.execute('SELECT version()')
    print(f'ClickHouse version: {version[0][0]}')
    table_content = """
    CREATE TABLE Exchange_Info (
    exchange String,
    symbol String,              
    assetType String, 
    tradingStatus UInt8,              
    createTime DateTime64(3),
    updateTime DateTime64(3),
    baseAsset String,              
    quoteAsset String,
    supportOrderType Array(String),              
    tickSize String,
    lotSize String,              
    marketLotSize String,
    minNotional String,              
    )        
    ENGINE = MergeTree
    ORDER BY updateTime; 
    """
    client.execute(table_content)
    print('Table created successfully.')

    symbol_info = {
        "symbol": "symbol",
        "asset_type": "",
        "tradingStatus": "",
        "create_time": "",
        "update_time": "",
        "base_asset": "baseAsset",
        "quote_asset": "quoteAsset",
        "support_order_type": "orderTypes",
        "tick_size": "tick_size",
        "lot_size": "step_size",
        "market_lot_size": "step_size",
        "min_notional": "minNotional"

    }

def create_monitor_quote_asset_kline_table():
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    version = client.execute('SELECT version()')
    print(f'ClickHouse version: {version[0][0]}')
    '''
    table_content = """
        CREATE TABLE Binance_Quote_Asset_Kline (
        symbol String,
        symbolMappingByte UInt16,
        exchange String,
        assetType String,
        openPrice Float64,
        highPrice Float64,
        lowPrice Float64,
        closePrice Float64,
        quoteAssetVolume Float64,
        openTime DateTime64(3),
        closeTime DateTime64(3),
        closeUsdtPrice Float64,
        )
        ENGINE = MergeTree
        ORDER BY closeTime; 
        """
    '''

    table_content = """
    CREATE TABLE Binance_Monitor_Quote_Asset_Kline (
    symbol String,
    symbolMappingByte Nullable(UInt16),
    exchange Nullable(String),
    assetType String,
    openPrice Nullable(Float64),
    highPrice Nullable(Float64),
    lowPrice Nullable(Float64),
    closePrice Nullable(Float64),
    quoteAssetVolume Nullable(Float64),
    openTime DateTime64(3),
    closeTime Nullable(DateTime64(3)),
    closeUsdtPrice Nullable(Float64)
    ) ENGINE = ReplacingMergeTree()
    ORDER BY (symbol,assetType,openTime);
    """
    client.execute(table_content)
    print('Table created successfully.')

def exchange_info_insert(data):
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    insert_data = []
    for record in data:
        insert_data.append((
            record["exchange"],
            record["symbol"],
            record["assetType"],
            record["tradingStatus"],
            record["createTime"],
            record["updateTime"],
            record["baseAsset"],
            record["quoteAsset"],
            record["supportOrderType"],
            record["tickSize"],
            record["lotSize"],
            record["marketLotSize"],
            record["minNotional"]
        ))
    print('test')
    print(insert_data)


    client.execute("""
        INSERT INTO Exchange_Info (
            exchange, symbol, assetType, tradingStatus, createTime, updateTime,
            baseAsset, quoteAsset, supportOrderType, tickSize, lotSize,
            marketLotSize, minNotional
        )
        VALUES
    """, insert_data)
    print("Insert Done.")
def test():
    # 创建 ClickHouse 客户端对象
    client = Client(host='localhost', port=9000, user='default', password='', database='default')

    # 测试连接
    try:
        # 执行查询：获取 ClickHouse 的版本号
        version = client.execute('SELECT version()')
        print(f'ClickHouse version: {version[0][0]}')

        # 创建一个测试表
        client.execute('CREATE TABLE IF NOT EXISTS test_table (id Int32, name String) ENGINE = Memory')
        print('Table created successfully.')

        # 插入数据
        client.execute('INSERT INTO test_table (id, name) VALUES', [(1, 'Alice'), (2, 'Bob')])
        print('Data inserted successfully.')

        # 查询数据
        result = client.execute('SELECT * FROM test_table')
        print('Query Result:', result)

    except Exception as e:
        print(f'Error: {e}')

def test_table():
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    result = client.execute('SELECT * FROM Exchange_Info LIMIT 1')
    print(result)

def database_executor(statement,client=None):
    if not client:
        client = global_variable_manager.get("clickhouse_client")
        if not client:
            client = Client(host='localhost', port=9000, user='default', password='', database='default')
            global_variable_manager.add(variable_name="clickhouse_client",variable_value=client)

    return client.execute(statement)

def insert_new_column(client=None):
    if not client:
        client = global_variable_manager.get("clickhouse_client")
        if not client:
            client = Client(host='localhost', port=9000, user='default', password='', database='default')
            global_variable_manager.add(variable_name="clickhouse_client",variable_value=client)

    table_name = "Exchange_Info"
    column_info = [ {'name': 'filterResult', 'type': 'UInt8', 'default': 0},
                 {'name': 'filterTime', 'type': 'DateTime64(3)', 'default': None},
                 {'name': 'mappingByte', 'type': 'UInt16', 'default': None}
                ]

    query_statement = []
    for column in column_info:
        if column['default'] is not None:
            query_statement.append(f"ADD COLUMN {column['name']} {column['type']} DEFAULT {column['default']}")
        else:
            query_statement.append(f"ADD COLUMN {column['name']} {column['type']}")

    query = f"ALTER TABLE {table_name} " + ", ".join(query_statement) + ";"

    try:
        client.execute(query)
        print(f"Columns added successfully to {table_name}!")
    except Exception as e:
        print(f"Error adding columns: {e}")

def insert_dataframe_to_table(table_name,df,column_order):
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    data = df.values.tolist()
    insert_query = f"INSERT INTO {table_name} ({', '.join(column_order)}) VALUES"
    client.execute(insert_query, data)
    print(f"Data successfully inserted into {table_name}!")

def create_tick_trade_table():
    pass

def create_symbol_mapping_table():
    client = Client(host='localhost', port=9000, user='default', password='', database='default')

    table_content = """
    CREATE TABLE Symbol_Mapping_Info (
    exchange String,                
    exchangeMappingInteger UInt8,    
    assetType String,                    
    symbol String,                   
    symbolMappingInteger UInt16,     
    mappingByte UInt16               
    ) ENGINE = MergeTree()
    ORDER BY (exchange, assetType, symbol);
    """
    client.execute(table_content)
    print('Table created successfully.')

def update_symbol_mapping_table():
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    version = client.execute('SELECT version()')
    print(f'ClickHouse version: {version[0][0]}')

    query = """
    SELECT
        exchange,
        assetType,
        symbol,
        exchangeMappingInteger,
        symbolMappingInteger
    FROM Symbol_Mapping_Info;
    """


    results = client.execute(query)


    data_to_update = []
    for row in results:
        exchange = row[0]
        assetType = row[1]
        symbol = row[2]
        exchangeMappingInteger = row[3]
        symbolMappingInteger = row[4]

        mappingByte= (exchangeMappingInteger << 11) | symbolMappingInteger
        data_to_update.append((exchange, assetType, symbol, mappingByte))


    for exchange, assetType, symbol, mappingByte in data_to_update:
        update_query = """
        ALTER TABLE Symbol_Mapping_Info
        UPDATE mappingByte = %s
        WHERE exchange = '%s' AND symbol = '%s' AND assetType = '%s';
        """ % (mappingByte, exchange, symbol, assetType)
        client.execute(update_query)

    #print("mappingInteger updated successfully!")

    print("symbolMappingInteger updated successfully!")

    #print("Batch update completed successfully!")

def create_tick_trade_table():
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    version = client.execute('SELECT version()')
    print(f'ClickHouse version: {version[0][0]}')

    content = """
    CREATE TABLE TickTrade (
    symbolMappingByte UInt16 Codec(Delta, ZSTD),     # 2 bytes, mapping exchange+assetType+symbol, 
	tradeId UInt32 Codec(Delta, ZSTD),                # 4 bytes, record the unique id from exchange ;
    tradingPrice Float32 Codec(Gorilla, ZSTD),        # 4 bytes, record the 10^{-6} precision price ;
    tradingPriceScale Enum8('1' = 1, '100' = 100) Codec(ZSTD),       # 1 byte, the real tradingPrice = tradingPrice * scale;
    tradingVolume Float32 Codec(Gorilla, ZSTD),        # 4 bytes,record the 10^{-6} precision volume ;
    tradingVolumeScale Enum8('1' = 1, '100' = 100) Codec(ZSTD),       # 1 byte, the real tradingPrice = tradingPrice * scale;
    baseTime DateTime32 Codec(DoubleDelta, ZSTD),          # 4 bytes, baseTime to record timestamp as second precition;
    deltaOffset UInt32 Codec(DoubleDelta, ZSTD),  # 4 bytes, record the microsecond delta addition ;
    isMaker UInt8 Codec(ZSTD),                 # 1 bytes, record if maker ;
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMMDD(baseTime)
    ORDER BY (symbolMappingByte, baseTime,deltaOffset);
    # the sum: 25 bytes ;
    """
    client.execute(content)
    print('TickTrade Table has successfully created.')

def test():
    client = Client(host='localhost', port=9000, user='default', password='', database='default')
    version = client.execute('SELECT version()')
    table_content = """
    
    CREATE TABLE OrderMarketDepth (
    symbolMappingByte UInt16 Codec(Delta, ZSTD),     
	updateId UInt32 Codec(Delta, ZSTD), 
    baseTime DateTime32 Codec(DoubleDelta, ZSTD),   
    deltaOffset UInt32 Codec(DoubleDelta, ZSTD), 
    priceScale Enum8('1' = 1, '100' = 100) Codec(ZSTD), 
    volumeScale Enum8('1' = 1, '100' = 100) Codec(ZSTD),
    ask1Price Float32 Codec(Gorilla),
    otherAsksPrice Array(Int16) Codec(Delta, ZSTD),
    ask1Volume Float32 Codec(Gorilla),
    otherAsksVolume Array(Int16) Codec(Delta, ZSTD),
    bid1Price Float32 Codec(Gorilla),
    otherBidsPrice Array(Int16) Codec(Delta, ZSTD),
    bid1Volume Float32 Codec(Gorilla),
    otherBidsVolume Array(Int16) Codec(Delta, ZSTD),
    ) ENGINE = MergeTree()
    PARTITION BY toYYYYMMDD(baseTime)
    ORDER BY (symbolMappingByte, baseTime, deltaOffset);
    # the sum: 25 bytes ;
    """

    client.execute(table_content)
    print('TickTrade Table has successfully created.')

def test_manager():
    manager = Clickhouse_Manager()


if __name__ == '__main__':
    test_manager()





