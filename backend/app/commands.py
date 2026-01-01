import click
from flask.cli import with_appcontext
from app.scrapers.reed import ReedScraper

@click.command('scrape-reed')
@with_appcontext
def scrape_reed_command():
    """Run the Reed.co.uk scraper."""
    click.echo('Starting Reed Scraper...')
    scraper = ReedScraper()
    scraper.run()
    click.echo('Scrape complete.')
