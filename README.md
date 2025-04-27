# Tweet Sentiment Analysis Project

This project provides a sentiment analysis tool for tweets using OpenAI's GPT model and PostgreSQL database. It allows users to analyze tweet sentiments and convert negative tweets to positive ones.

## Features

- Tweet sentiment analysis using OpenAI GPT
- Negative to positive tweet conversion
- PostgreSQL database integration
- Real-time tweet processing
- Emoji detection and analysis
- Case-insensitive username search
- Batch processing for large datasets

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- OpenAI API key
- Required Python packages (listed in requirements.txt)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd <project-directory>
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the project root with:
```
OPENAI_API_KEY=your_openai_api_key
```

## Database Configuration

1. Create a PostgreSQL database named `tweets_dataset`
2. Update database credentials in `db_config.py`:
```python
DB_CONFIG = {
    'dbname': 'tweets_dataset',
    'user': 'your_username',
    'password': 'your_password',
    'host': 'localhost',
    'port': '5432'
}
```

## Dataset Import

1. Place your tweet dataset CSV file in the `dataset` directory
2. Update the CSV file path in `db_config.py`:
```python
csv_file_path = "path/to/your/dataset.csv"
```

3. Run the database migration:
```bash
python db_config.py
```

## Project Structure

```
project/
├── dataset/
│   └── training.1600000.processed.noemoticon.csv
├── db_config.py
├── sentiment_analysis.py
├── requirements.txt
├── .env
└── README.md
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run sentiment_analysis.py
```

2. Enter a Twitter username (without @) in the input field
3. View tweets and their details
4. Use the following features:
   - Analyze sentiment of tweets
   - Convert negative tweets to positive
   - View processed tweet text
   - See emoji analysis

## Features in Detail

### Tweet Analysis
- Processes tweets to remove URLs, mentions, and hashtags
- Detects and analyzes emojis
- Provides detailed sentiment analysis
- Shows both original and processed tweet text

### Database Operations
- Stores tweets with sentiment information
- Maintains tweet metadata (ID, date, query)
- Supports batch processing for large datasets
- Case-insensitive username search

### User Interface
- Clean, intuitive Streamlit interface
- Real-time tweet display
- Interactive sentiment analysis
- Immediate feedback on conversions

## Error Handling

The application includes comprehensive error handling for:
- Database connection issues
- Invalid usernames
- API errors
- Data processing errors
- File access problems

## Performance Considerations

- Batch processing for large datasets
- Efficient database queries
- Caching for improved performance
- Memory-efficient tweet processing

## Security

- Environment variables for sensitive data
- Database credential protection
- API key security
- Input validation and sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the repository or contact the maintainers.

## Acknowledgments

- OpenAI for the GPT API
- Streamlit for the web interface
- PostgreSQL for the database
- Contributors and maintainers 