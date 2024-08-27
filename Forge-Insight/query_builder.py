from typing import List, Dict, Any
from config import SCHEMA, MAX_QUERY_LIMIT
import time
import re

class QueryBuilder:
    def __init__(self):
        self.schema = SCHEMA

    def build_query(self, entity: str, fields: List[str], filters: Dict[str, Any] = None, limit: int = 100) -> str:
        if entity not in self.schema:
            raise ValueError(f"Invalid entity: {entity}")

        # Validate fields
        valid_fields = set(self.schema[entity]['fields'].keys())
        invalid_fields = set(fields) - valid_fields
        if invalid_fields:
            raise ValueError(f"Invalid fields for {entity}: {', '.join(invalid_fields)}")

        # Validate and sanitize filters
        if filters:
            filters = self.validate_and_sanitize_filters(entity, filters)

        # Enforce maximum limit
        limit = min(limit, MAX_QUERY_LIMIT)

        # Build the query string
        query = f"query {{\n"
        query += f"  {entity.lower()}s"
        
        # Add filters and limit
        args = []
        if filters:
            filter_str = self._build_filter_string(filters)
            if filter_str:
                args.append(f"where: {{{filter_str}}}")
        args.append(f"first: {limit}")
        if args:
            query += f"({', '.join(args)})"

        # Add fields
        query += " {\n"
        for field in fields:
            query += f"    {field}\n"
        query += "  }\n"
        query += "}"

        print(f"Final built query: {query}")
        return query

    def _build_filter_string(self, filters: Dict[str, Any]) -> str:
        """
        Builds a filter string for GraphQL queries.

        :param filters: Dictionary of filters
        :return: A formatted filter string
        """
        filter_parts = []
        for key, value in filters.items():
            if isinstance(value, str):
                filter_parts.append(f"{key}: \"{value}\"")
            elif isinstance(value, (int, float)):
                filter_parts.append(f"{key}: {value}")
            elif isinstance(value, bool):
                filter_parts.append(f"{key}: {str(value).lower()}")
            elif isinstance(value, dict):
                nested_filter = self._build_filter_string(value)
                filter_parts.append(f"{key}: {{{nested_filter}}}")
            elif isinstance(value, list):
                list_values = ", ".join([f'"{v}"' if isinstance(v, str) else str(v) for v in value])
                filter_parts.append(f"{key}: [{list_values}]")

        return ", ".join(filter_parts)

    def validate_and_sanitize_filters(self, entity: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        valid_filters = {}
        for key, value in filters.items():
            if key not in self.schema[entity]['fields']:
                raise ValueError(f"Invalid filter key for {entity}: {key}")
            
            # Sanitize string values
            if isinstance(value, str):
                value = re.sub(r'[^\w\s-]', '', value)  # Remove special characters
            
            valid_filters[key] = value
        
        return valid_filters

    def get_available_entities(self) -> List[str]:
        """
        Returns a list of available entities from the schema.

        :return: List of entity names
        """
        return list(self.schema.keys())

    def get_entity_fields(self, entity: str) -> List[str]:
        """
        Returns a list of available fields for a given entity.

        :param entity: The entity name
        :return: List of field names
        """
        if entity not in self.schema:
            raise ValueError(f"Invalid entity: {entity}")
        return list(self.schema[entity]['fields'].keys())

    def get_field_description(self, entity: str, field: str) -> str:
        """
        Returns the description of a specific field for a given entity.

        :param entity: The entity name
        :param field: The field name
        :return: Field description
        """
        if entity not in self.schema or field not in self.schema[entity]['fields']:
            raise ValueError(f"Invalid entity or field: {entity}.{field}")
        return self.schema[entity]['fields'][field]

    def build_custom_unique_traders_query(self, pool_address: str, days: int = 180, interval: int = 30):
        current_timestamp = int(time.time())
        start_timestamp = current_timestamp - (days * 86400)  # 86400 seconds in a day
        
        query = f"""
        query {{
          swaps(
            where: {{
              pool: "{pool_address}",
              timestamp_gte: {start_timestamp},
              timestamp_lte: {current_timestamp}
            }}
            first: 1000
            orderBy: timestamp
            orderDirection: asc
          ) {{
            origin
            timestamp
          }}
        }}
        """
        print(f"Debug: Generated query: {query}")
        return query