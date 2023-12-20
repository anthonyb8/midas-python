import databento as db
from enum import Enum
from decouple import config
from database import DatabaseClient
import pandas as pd

class Schemas(Enum):
    MBO='mbo'               # Market by order, full order book, tick data
    MBP_10='mbp-10'	        # L2, market by price, market depth
    MBP_1='mbp-1'	        # L1, top of book, trades and quotes
    TBBO='tbbo'	            # Top of book, sampled in trade space
    Trades='trades'	        # Last sale, time and sales, tick-by-tick trades
    OHLCV_1s='ohlcv-1s'     # OHLCV bars, aggregates
    OHLCV_1m='ohlcv-1m'     # OHLCV bars, aggregates
    OHLCV_1h='ohlcv-1h'     # OHLCV bars, aggregates
    OHLCV_1d='ohlcv-1d'     # OHLCV bars, aggregates
    Definition='definition'	# Security definitions, reference data, symbol list
    Imbalance='imbalance'	# Imbalance auction quotes
    Statistics='statistics' 

class Symbology(Enum):
    RAWSYMBOL='raw_symbol'         # Original string symbols used by the publisher in the source data.
    INSTRUMENT_ID='instrument_id'  # Unique numeric ID assigned to each instrument by the publisher.
    PARENTSYMBOL='parent'          # Groups instruments related to the market for the same underlying.
    CONTINUOSCONTRACT='continuous' # Proprietary symbology that specifies instruments based on certain systematic rules.

class Datasets(Enum):   
    NASDAQ='XNAS.ITCH'               # Nasdaq TotalView-ITCH is the proprietary data feed that provides full order book depth for Nasdaq market participants.
    CME='GLBX.MDP3'                  # MDP 3.0 is the sole data feed for all instruments traded on CME Globex, including futures, options, spreads and combinations.
    OPRA='OPRA.PILLAR'               # Options data. Consolidated last sale, exchange BBO and national BBO across all US equity options exchanges
    DATABENTOEQUITIES='DBEQ.BASIC'   # A consolidation of US equities prop feeds that’s free to license for all use cases. 
    
class DBClientManager:
    def __init__(self, symbols:list, schema:Schemas,dataset:Datasets,stype:Symbology, start_date=None, end_date=None):
        self.symbols=symbols
        self.schema=schema.value
        self.dataset=dataset.value
        self.stype = stype.value
        self.start_date=start_date
        self.end_date=end_date
        self.hist_client=None
        self.live_client=None

    def _set_historical_client(self):
        self.hist_client = db.Historical(config('DATABENTO_API_KEY'))

    def get_data(self):
        # Initialize historical client if not already done
        if not self.hist_client:
            self._set_historical_client()

        # Get the cost of data pull
        cost = self.get_cost()

        # Confirm cost with the user, with a maximum of 3 attempts to avoid infinite loop
        max_attempts = 3
        for attempt in range(max_attempts):
            answer = input(f"\nThe cost of this data pull will be ${cost}. Would you like to proceed? (Y/n): ")
            if answer.lower() == 'n':
                print("Data pull cancelled by user.")
                return
            elif answer.lower() == 'y':
                break
            else:
                print("Invalid input. Please enter 'Y' to proceed or 'n' to cancel.")
                if attempt == max_attempts - 1:
                    print("Maximum attempts reached. Data pull cancelled.")
                    return

        # Check the size of the data
        if self.get_size() < 5:
            # If less than 5 GB, proceed with historical data retrieval
            return self.get_historical()
        else:
            # Suggest batch load for large data sizes
            print("\nData size greater than 5 GB: Batch Load Recommended.")
            # Here you can add logic for batch loading if applicable

    def get_historical(self):
        """ Used to return smaller batches of data under """
        try:                
            data = self.hist_client.timeseries.get_range(
                dataset=self.dataset,
                symbols=self.symbols,
                schema=self.schema,
                start=self.start_date,
                end=self.end_date,
            )

            # Convert to DataFrame
            df = data.to_df()
            df.reset_index(inplace=True) 
            df.rename(columns={"ts_event": "timestamp"}, inplace=True) 

            # Drop the unnecessary columns
            columns_to_drop = ['publisher_id', 'rtype', 'instrument_id']
            df.drop(columns=columns_to_drop, errors='ignore', inplace=True)
                    
            # Convert the DataFrame to JSON, with dates in ISO format
            df['timestamp'] = df['timestamp'].apply(lambda x: x.isoformat() if pd.notnull(x) else None)
            data_list = df.to_dict(orient='records')
            
            return data_list
        
        except Exception as e:
            print(f"An error occurred: {e}")
            raise
    
    def get_batch(self):
        data = self.hist_client.batch.submit_job(
            dataset=self.datasets,
            symbols=self.symbols,
            schema=self.schemas,
            encoding="dbn",
            start=self.start_date,
            end=self.end_date,
        )

    def get_size(self):
        """ Returns data size in GBs."""
        size = self.hist_client.metadata.get_billable_size(
            dataset=self.dataset,
            symbols=self.symbols,
            schema=self.schema,
            start=self.start_date,
            end=self.end_date,
            stype_in = self.stype,
        )

        # logger.info(f"\n Bytes: {size} | KB:{size/10**3} | MB: {size/10**6} | GB: {size/10**9}\n")
        
        return size/10**9
    
    def get_cost(self):
        """ Cost returned in USD."""
        cost = self.hist_client.metadata.get_cost(
            dataset=self.dataset,
            symbols=self.symbols,
            schema=self.schema,
            start=self.start_date,
            end=self.end_date,
        )

        return cost

    def get_live(self):
        """TODO : Add live feed later. """
        self.live_client = db.Live(config('DATABENTO_API_KEY'))


if __name__ == "__main__":
    start_date = '2023-01-01'
    end_date = '2023-03-01'
    schema = Schemas.OHLCV_1d
    dataset = Datasets.NASDAQ
    stype = Symbology.RAWSYMBOL
    symbols = ['AAPL', 'MSFT']

    # Initialize the database client
    database = DatabaseClient(api_url='http://127.0.0.1:8000')  # Adjust URL if not running locally

    # Check and create assets if they don't exist
    for symbol in symbols:
        if not database.get_asset_by_symbol(symbol):
            database.create_asset(symbol=symbol, asset_type="equity")

    # Databento client
    client = DBClientManager(symbols, schema, dataset, stype, start_date, end_date)
    data = client.get_data()
    
    # Database client
    response = database.create_bulk_price_data(data)