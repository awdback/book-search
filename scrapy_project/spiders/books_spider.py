import scrapy
import json

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']
    
    def parse(self, response):
        # Extract book links dari halaman utama
        book_links = response.css('article.product_pod h3 a::attr(href)').getall()
        
        # Follow setiap link buku
        for link in book_links:
            yield response.follow(link, self.parse_book)
        
        # Follow pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)
    
    def parse_book(self, response):
        # Extract informasi detail buku
        title = response.css('h1::text').get()
        price = response.css('p.price_color::text').get()
        availability = response.css('p.availability::text').re_first(r'(\d+)')
        rating = response.css('p.star-rating::attr(class)').re_first(r'star-rating (\w+)')
        description = response.css('#product_description ~ p::text').get()
        category = response.css('ul.breadcrumb li:nth-child(3) a::text').get()
        
        # Konversi rating ke angka
        rating_map = {
            'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5
        }
        rating_num = rating_map.get(rating, 0)
        
        yield {
            'title': title,
            'price': price,
            'availability': availability,
            'rating': rating_num,
            'description': description,
            'category': category,
            'url': response.url
        }
