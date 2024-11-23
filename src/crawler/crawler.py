import asyncio
import re
from urllib.parse import urljoin
import httpx
from bs4 import BeautifulSoup

class PageContent:
	def __init__(self,
				divs: list[str] = list(),
				paragraphs: list[str] = list(),
				headings: list[str] = list(),
				lists: list[str] = list(),
				url: str = "",
				links: list[str] = list(),
			):
		self._divs = divs
		self._paragraphs = paragraphs
		self._headings = headings
		self._lists = lists
		self._url = url
		self._links = links

	def url(self) -> str:
		return self._url
	
	def divs(self) -> list[str]:
		return self._divs

	def paragraphs(self) -> list[str]:
		return self._paragraphs
	
	def headings(self) -> list[str]:
		return self._headings

	def links(self) -> set[str]:
		return self._links

	def lists(self) -> set[str]:
		return self._lists

	def construct_text(self) -> str:
		result = []
		
		result.append(f"URL:\n{self.url()}\n")
		
		if self.headings():
			result.append("Headings:")
			for idx, heading in enumerate(self.headings(), 1):
				result.append(f"{idx}. {heading}")
			result.append("")
		
		if self.paragraphs():
			result.append("Paragraphs:")
			for paragraph in self.paragraphs():
				result.append(paragraph)
			result.append("")

		if self.divs():
			result.append("Divs:")
			for div in self.divs():
				result.append(div)
			result.append("")
		
		if self.lists():
			result.append("Lists:")
			for list_content in self.lists():
				result.append(list_content)
			result.append("")


		if self.links():
			result.append("Links:")
			for link in self.links():
				result.append(f"- {link}")
			result.append("")
		
		return "\n".join(result)

def _clean_url(link: str) -> str:
	link = re.sub(r'(#.*)', '', link)
	link = link.rstrip('/')
	return link

def _link_has_extension(url: str) -> bool:
	return bool(re.search(r'\.\w{3,4}($|\?)$', url))

async def _extract_page(url: str) -> PageContent:
	try:
		async with httpx.AsyncClient(follow_redirects=True) as client:
			response = await client.get(url, timeout=10)
			if response.status_code == 200:
				soup = BeautifulSoup(response.content, 'html.parser')
				paragraphs: list[str] = [p.text.strip() for p in soup.find_all('p')]
				links: list[str] = {urljoin(url, a['href']) for a in soup.find_all('a', href=True)}
				headings: list[str] = [h.text.strip() for h in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]
				lists: list[str] = [li.text.strip() for li in soup.find_all('li')]

				divs: list[str] = []
				descending_length_sorted_divs = sorted(soup.find_all('div'), key=lambda div: len(div.get_text(separator=" ", strip=True)), reverse=True)
				for div in descending_length_sorted_divs:
					div_text: str = div.get_text(separator=" ", strip=True)
					sentences = div_text.split(".")
					for sentence in sentences:
						text = sentence.strip()
						if (
								text and len(text) > 5 and
								not any(text in existing_text for existing_text in divs)
							):
							divs.append(text)
	
				return PageContent(divs, paragraphs, headings, lists, url, links)
	except Exception as e:
		print(f"Failed to fetch '{url}': {e}")
	return PageContent()


async def _crawl_page(url: str, base_url: str, visitedUrls: set, max_depth: int, current_depth=0) -> dict[str, str]:
	url = _clean_url(url)
	if current_depth > max_depth or url in visitedUrls or _link_has_extension(url) or not url.startswith('http') or not url.startswith(base_url):
		return {}
	
	visitedUrls.add(url)

	pageContext = await _extract_page(url)
	if len(pageContext.paragraphs()) == 0:
		return {}
	pageText = pageContext.construct_text()
	crawled_data = {pageContext.url(): pageText}

	new_depth = current_depth + 1
	
	tasks = []
	for link in pageContext.links():
		tasks.append(_crawl_page(link, base_url, visitedUrls, max_depth, new_depth))
	
	results = await asyncio.gather(*tasks)
	for result in results:
		crawled_data.update(result)
	
	return crawled_data

async def crawl_site(base_url: str, max_depth=7) -> dict[str, str]:
	"Use max depth based on how deep you want to crawl the site"
	site_data = await _crawl_page(base_url, base_url, set(), max_depth)
	print(f"Crawled '{len(site_data)}' pages with total length of text '{len(f"{site_data}")}'")
	return site_data
