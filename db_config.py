import psycopg2
from psycopg2 import Error
import os
import csv
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'dbname': 'tweets_dataset',
    'user': 'postgres',
    'password': 'postgres',  # You should change this to your actual password
    'host': 'localhost',
    'port': '5432'
}

def get_db_connection():
    try:
        connection = psycopg2.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Failed to connect to database: {str(e)}")
        return None

def create_tweets_table(connection):
    try:
        cursor = connection.cursor()
        
        # Create tweets table with columns matching the dataset
        create_table_query = """
        CREATE TABLE IF NOT EXISTS tweets (
            id SERIAL PRIMARY KEY,
            sentiment INTEGER,
            tweet_id BIGINT,
            tweet_date TIMESTAMP,
            query VARCHAR(255),
            username VARCHAR(255),
            tweet_text TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(create_table_query)
        connection.commit()
        
    except Error as e:
        print(f"Error creating table: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()

def parse_date(date_str):
    try:
        return datetime.strptime(date_str, '%a %b %d %H:%M:%S PDT %Y')
    except ValueError:
        try:
            return datetime.strptime(date_str, '%a %b %d %H:%M:%S PST %Y')
        except ValueError:
            print(f"Could not parse date: {date_str}")
            return None

def import_tweets_from_csv(connection, csv_file_path):
    try:
        cursor = connection.cursor()
        
        # Check if file exists
        if not os.path.exists(csv_file_path):
            print(f"CSV file not found: {csv_file_path}")
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        # Read and import the CSV file
        with open(csv_file_path, 'r', encoding='latin-1') as file:
            csv_reader = csv.reader(file)
            batch_size = 1000
            batch = []
            
            for row in csv_reader:
                if len(row) >= 6:  # Ensure we have all required columns
                    try:
                        sentiment = int(row[0])
                        tweet_id = int(row[1])
                        tweet_date = parse_date(row[2])
                        query = row[3]
                        username = row[4]
                        tweet_text = row[5]
                        
                        batch.append((
                            sentiment,
                            tweet_id,
                            tweet_date,
                            query,
                            username,
                            tweet_text
                        ))
                        
                        if len(batch) >= batch_size:
                            cursor.executemany("""
                                INSERT INTO tweets 
                                (sentiment, tweet_id, tweet_date, query, username, tweet_text)
                                VALUES (%s, %s, %s, %s, %s, %s)
                            """, batch)
                            connection.commit()
                            print(f"Imported {len(batch)} records")
                            batch = []
                            
                    except (ValueError, IndexError) as e:
                        print(f"Skipping invalid row: {row}. Error: {str(e)}")
                        continue
            
            # Insert any remaining records
            if batch:
                cursor.executemany("""
                    INSERT INTO tweets 
                    (sentiment, tweet_id, tweet_date, query, username, tweet_text)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, batch)
                connection.commit()
                print(f"Imported final {len(batch)} records")
        
        # Verify data import
        cursor.execute("SELECT COUNT(*) FROM tweets;")
        count = cursor.fetchone()[0]
        print(f"Total records imported: {count}")
        
    except Error as e:
        print(f"Error importing data: {str(e)}")
        connection.rollback()
        raise
    except Exception as e:
        print(f"Unexpected error during import: {str(e)}")
        connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()

def run_migration():
    """Main function to run the database migration"""
    print("Starting database migration process")
    
    # Database connection
    connection = get_db_connection()
    if not connection:
        print("Failed to connect to the database. Please check your database configuration.")
        return
    
    try:
        # Create the tweets table
        create_tweets_table(connection)
        
        # Import data from CSV
        csv_file_path = r"G:\External Work\University Work\Semester 8\FYP_LLM_Based\dataset\training.1600000.processed.noemoticon.csv"
        import_tweets_from_csv(connection, csv_file_path)
        
        print("Database migration completed successfully")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
    finally:
        if connection:
            connection.close()
            print("Database connection closed")

if __name__ == "__main__":
    try:
        run_migration()
    except KeyboardInterrupt:
        print("Process interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}") 