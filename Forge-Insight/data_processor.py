import pandas as pd

class DataProcessor:
    @staticmethod
    def process_data(data):
        processed_data = {}
        for key, value in data.items():
            if isinstance(value, list) and value:
                df = pd.DataFrame(value)
                processed_data[key] = {
                    'dataframe': df,
                    'summary': DataProcessor.generate_summary(df),
                    'stats': DataProcessor.calculate_stats(df)
                }
            else:
                processed_data[key] = value
        return processed_data

    @staticmethod
    def generate_summary(df):
        return df.describe()

    @staticmethod
    def calculate_stats(df):
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        stats = {
            'mean': df[numeric_columns].mean().to_dict(),
            'median': df[numeric_columns].median().to_dict(),
            'std': df[numeric_columns].std().to_dict(),
            'min': df[numeric_columns].min().to_dict(),
            'max': df[numeric_columns].max().to_dict()
        }
        return stats

    @staticmethod
    def filter_data(df, filters):
        for column, value in filters.items():
            if column in df.columns:
                df = df[df[column] == value]
        return df

    @staticmethod
    def sort_data(df, sort_by, ascending=True):
        if sort_by in df.columns:
            return df.sort_values(by=sort_by, ascending=ascending)
        return df

    @staticmethod
    def aggregate_data(df, group_by, agg_func):
        if group_by in df.columns:
            return df.groupby(group_by).agg(agg_func)
        return df