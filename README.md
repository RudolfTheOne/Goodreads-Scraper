Goodreads scraper.

Two main configuration options:

URL: (default: https://www.goodreads.com/shelf/show/conspiracy) - point to the category you want to download

count: (default: 30) - maximum number of pages to process

EMAIL: your goodreads account email used for login purposes

Gets following data:

['title', 'author', 'booklink', 'ratingscount', 'rating', 'genre1', 'genre2', 'genre3', 'genre4']

run with: 

scrapy crawl goodreads_ratings --set FEED_URI=output.csv --set FEED_FORMAT=csv -a password=your_goodreads_account_password

