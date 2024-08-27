import requests
from requests.exceptions import RequestException
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time
from config import API_TIMEOUT, ERROR_MESSAGES, SUBGRAPH_URLS, SCHEMA
from subgraph_schemas.forge_subgraph_schema import SUBGRAPH_SCHEMA as FORGE_SUBGRAPH_SCHEMA
from collections import defaultdict
from query_builder import QueryBuilder

SUBGRAPH_SCHEMAS = {
    "Forge": FORGE_SUBGRAPH_SCHEMA,
    # Add other subgraphs here as they are supported
}

class SubgraphConnector:
    def __init__(self):
        self.session = requests.Session()
        self.current_subgraph = list(SUBGRAPH_URLS.keys())[0]  # Set default subgraph
        self.schema = SCHEMA
        self.subgraph_schemas = SUBGRAPH_SCHEMAS
        self.query_builder = QueryBuilder()

    def get_current_subgraph_schema(self):
        return self.subgraph_schemas.get(self.current_subgraph, {})

    def get_subgraph_list(self):
        return list(SUBGRAPH_URLS.keys())

    def set_current_subgraph(self, subgraph):
        self.current_subgraph = subgraph

    def get_active_subgraph_url(self):
        return SUBGRAPH_URLS.get(self.current_subgraph, "")

    def get_entities(self):
        return list(self.schema.keys())

    def get_entity_fields(self, entity):
        return list(self.schema[entity]['fields'].keys())

    def get_field_description(self, entity, field):
        return self.schema[entity]['fields'][field]

    def build_query(self, entity: str, fields: list, address: Optional[str] = None, limit: int = 100, 
                    order_by: Optional[str] = None, order_direction: str = "asc", 
                    time_filter: Optional[str] = None, custom_filter: Optional[str] = None) -> str:
        where_conditions = []
        if address:
            if entity in ['Pool', 'Token']:
                where_conditions.append(f'id: "{address}"')
            elif entity == 'Swap':
                where_conditions.append(f'pool: "{address}"')
            elif entity == 'Position':
                where_conditions.append(f'owner: "{address}"')
            elif entity == 'PoolDayData':
                where_conditions.append(f'pool: "{address}"')

        # Only apply time filter for entities that support it
        if time_filter and entity.lower() not in ['factory', 'factories']:
            time_condition = self._get_common_filter_condition(time_filter)
            if time_condition:
                where_conditions.append(time_condition)
            print(f"Time filter condition: {time_condition}")  # Debug print
        
        if custom_filter:
            where_conditions.append(custom_filter)

        where_clause = f'where: {{ {", ".join(where_conditions)} }}' if where_conditions else ''
        order_condition = f'orderBy: {order_by}, orderDirection: {order_direction.lower()}' if order_by else ''

        # Handle pluralization
        if entity.lower() == 'factory':
            entity_plural = 'factories'
        else:
            entity_plural = entity.lower() + ('ies' if entity.lower().endswith('y') else 's')

        query = f"""
          query {{
            {entity_plural}(first: {limit}, {where_clause} {order_condition}) {{
              {' '.join(fields)}
            }}
          }}
        """
        print(f"Generated query: {query}")  # Debug print
        return query.strip()

    def _get_common_filter_condition(self, common_filter: str) -> str:
        now = int(datetime.utcnow().timestamp())  # Use seconds instead of milliseconds
        if common_filter == 'Last 24 hours':
            start_time = now - 24 * 60 * 60
        elif common_filter == 'Last 7 days':
            start_time = now - 7 * 24 * 60 * 60
        elif common_filter == 'Last 30 days':
            start_time = now - 30 * 24 * 60 * 60
        else:  # All time
            return ''
        
        return f'timestamp_gte: {start_time}'

    def build_unique_traders_query(self, address: Optional[str], limit: int, time_range: str) -> str:
        time_filter = self._get_common_filter_condition(time_range)
        where_conditions = [time_filter] if time_filter else []
        
        if address:
            where_conditions.append(f'pool: "{address}"')

        where_clause = f'where: {{ {", ".join(where_conditions)} }}' if where_conditions else ''

        query = f"""
          query {{
            swaps(first: {limit}, {where_clause}) {{
              origin
              timestamp
              pool {{
                id
              }}
              transaction {{
                id
              }}
            }}
          }}
        """
        
        print(f"Generated unique traders query: {query}")  # Debug print
        return query.strip()

    def query_subgraph(self, query: str) -> Dict[str, Any]:
        url = self.get_active_subgraph_url()
        print(f"Querying subgraph URL: {url}")

        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            try:
                response = self.session.post(url, json={'query': query}, timeout=API_TIMEOUT)
                response.raise_for_status()
                data = response.json()

                print(f"Raw response data: {data}")

                if 'errors' in data:
                    error_message = data['errors'][0]['message'] if data['errors'] else "Unknown error occurred"
                    print(f"GraphQL error: {error_message}")
                    raise ValueError(ERROR_MESSAGES['api_error'].format(error_message))
                
                if 'data' not in data:
                    print("No data returned in the response")
                    raise ValueError(f"No data returned for query")

                return self.process_query_results(data['data'])

            except RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Network error occurred. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise Exception(f"Network error after {max_retries} attempts: {str(e)}")
            except Exception as e:
                print(f"Error in query_subgraph: {str(e)}")
                print(f"Query: {query}")
                raise

    def process_query_results(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the query results before returning them.
        This method can be extended to perform any necessary data transformations or validations.

        :param data: The raw data returned from the subgraph query
        :return: Processed data
        """
        # For now, we'll just return the data as is
        # You can add any processing logic here in the future
        return data

    def run_wallet_overview_query(self, wallet_address: str, limit: int = 100):
        print(f"Running wallet overview query for address: {wallet_address}")
        swap_fields = ['id', 'timestamp', 'origin', 'pool', 'token0', 'token1', 'amount0', 'amount1', 'amountUSD']
        position_fields = ['id', 'owner', 'pool', 'token0', 'token1', 'liquidity', 'depositedToken0', 'depositedToken1', 'withdrawnToken0', 'withdrawnToken1', 'collectedFeesToken0', 'collectedFeesToken1']

        swap_query = self.build_query("Swap", swap_fields, {"origin": wallet_address}, limit)
        position_query = self.build_query("Position", position_fields, {"owner": wallet_address}, limit)

        combined_query = f"query {{ {swap_query} {position_query} }}"
        print(f"Combined query: {combined_query}")
        return self.query_subgraph(combined_query)

    def query_unique_traders(self, pool_address: str, days: int = 180, interval: int = 30):
        query = self.query_builder.build_custom_unique_traders_query(pool_address, days, interval)
        raw_data = self.query_subgraph(query)

        swaps = raw_data.get('swaps', [])
        
        print(f"Debug: Received {len(swaps)} swaps")
        
        total_unique_traders = set()
        interval_traders = defaultdict(set)
        processed_swaps = []
        
        end_timestamp = int(time.time())
        start_timestamp = end_timestamp - (days * 86400)
        
        print(f"Debug: Start timestamp: {start_timestamp}, End timestamp: {end_timestamp}")
        
        for swap in swaps:
            trader = swap['origin']
            timestamp = int(swap['timestamp'])
            
            print(f"Debug: Processing swap - Trader: {trader}, Timestamp: {timestamp}")
            processed_swaps.append({'trader': trader, 'timestamp': timestamp})
            
            if timestamp < start_timestamp:
                print(f"Debug: Skipping swap (timestamp too old)")
                continue
            
            total_unique_traders.add(trader)
            
            interval_index = (timestamp - start_timestamp) // (interval * 86400)
            interval_traders[interval_index].add(trader)
        
        print(f"Debug: Total unique traders: {len(total_unique_traders)}")
        print(f"Debug: Intervals: {dict(interval_traders)}")
        
        results = {
            'total_unique_traders': len(total_unique_traders),
            'interval_data': [
                {
                    'start_date': datetime.fromtimestamp(start_timestamp + (i * interval * 86400)).strftime('%Y-%m-%d'),
                    'end_date': datetime.fromtimestamp(min(start_timestamp + ((i+1) * interval * 86400), end_timestamp)).strftime('%Y-%m-%d'),
                    'unique_traders': len(traders)
                }
                for i, traders in sorted(interval_traders.items())
            ],
            'total_swaps': len(swaps),
            'start_timestamp': start_timestamp,
            'end_timestamp': end_timestamp,
            'processed_swaps': processed_swaps
        }
        
        return results