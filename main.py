from scraper import scrape_data
from csv_formatter import formatter

#* This is the main file of the program

def main() -> None:
    URL = 'https://www.geekwire.com/fundings/'

    print('Start scraping data from %s' % URL)
    print('Scraping in progress...')
    # scrape_data(URL, step=8)
    print('Done scraping!')
    
    print('Start formatting...')
    formatter()
    print('Done formatting!')

    print('Exiting...')


if __name__ == '__main__':
    main()
