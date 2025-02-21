
# 1-Project Overview
**Data Monitor System (DSM)** is one of vital components of Cobweb System, which is expected to implement all operations of data in a trading system. Data Monitor System is mainly designed for fetching data from exchanges, unifying data in designated rules and publishing data to all data consumers. 

# 2-Naming Convention
**Naming Convention in DataBase:**
1. **Tables** in DataBase: name in upper case naming like `Binance_Parser` ;
2. **Fields** in Table: name in lower case naming like `tradingPrice` ;

**Naming Convention in Python Files:**
1. **Modules, Folders and Class**es: name in underscore upper case like `Fetch_Websocket` ;
2. **Methods**: name in underscore lower case like `fetch_task` ;
3. **Variable**: name in underscore lower case like `asset_type` ;

# 3-Core Design Architecture


**Design & Planning Overview**:
As stated above, Data Monitor System (DMS) only focus on fetching, unifying and publishing, so the DMS takes Generator-Consumer design pattern to decouple data-fetch from data-consume.
In the light of accelerating running efficiency, DMS follows:
* (1) **Only Unifying**: decoupling from complex data processings such as data cleaning, filtering, aggregating and feature computing, but only focusing on mapping data into unified formats ;
* (2) **Transfer in Capnp Struct**: parsing and transferring data as Capnp structs with respect to space and speed ;
* (3) **Scalability as Local Configuration Files**: all scaleable designs show up as local configuration files, i.e., all URL information of exchanges, parsing information and mapping information are designated as a set of configuration files for a exchange.


**Some Key Modules**

**Module-Fetch_Data:** as the generator, fetch original data from exchanges, and expose original data to the outer modules ;

**Module-Parse_Data**: parse original data from exchanges to the binary format (Capnp Struct);

**Module-Alert_Monitor**: this module is only to monitor the basic running status, `expectional operation` / `normal operation` while running gather tasks.

Follow the decoupling principle, **central_data_manager** connects all modules of data generating and publishing.


# 4-Developing Journal & Version Overview

**Developing Planning**: 
1. **DMS version-1.x** : monitor the spot of Binance, test DMS's performance and detect potential flaws;
2. **DMS version-2.x**: monitor all asset of Binance, test DMS's reliability and scalability ;
3. **DMS version-3.x**: monitor multiple exchanges, access Grafana as the monitor terminal ;


**Developing Journal**:
1. Jerry-2025/02/18: upload DMS v-1.1.0, waiting the further testing results;

