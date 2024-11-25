import openai as openai

MAX_TEXT_LENGTH = 196_000

class Response:
	def __init__(self, answer: str|None, refusal: bool, input_tokens: int, output_tokens: int, sources: list[str]):
		self.answer = answer
		self.refusal = refusal
		self.input_tokens = input_tokens
		self.output_tokens = output_tokens
		self.sources = sources

class OpenAI:
	client = openai.OpenAI()
	
	def __init__(self, website_to_pages_to_data: dict[str, dict[str, str]]):
		self.website_to_pages_to_data = website_to_pages_to_data

	def ask(self, website: str, question: str) -> Response:
		site_data = _enforce_site_data_limit(self.website_to_pages_to_data[website].copy())
		response = self.client.beta.chat.completions.parse(
			model="gpt-4o-mini",
			messages=[
			{"role": "system", "content": (
				"You are an AI assistant trained to answer questions based on the information provided "
				"from the crawled website. You should answer as accurately as possible based solely on "
				"the content of the website data, without including any outside information. If the question "
				"cannot be answered based on the provided data, indicate that clearly."
			)},
			{"role": "user", "content": (
				f"I have the following site data available, which is about the website '{website}'. "
				"Please read through the data and answer the following question: \n\n"
				f"Website data:\n\n{site_data}\n\nQuestion: {question}\n"
				"Provide a clear and concise answer based on the information above."
			)}
		],
		)

		answer = response.choices[0].message
		usage = response.usage.to_dict()

		return Response(
			answer.content,
			bool(answer.refusal),
			int(usage.get("prompt_tokens")),
			int(usage.get("completion_tokens")),
			list((site_data).keys())
		)

def _enforce_site_data_limit(site_data: dict[str, str]) -> dict[str, str]:
	site_data_with_data_limit = site_data.copy()
	total_text_length = len(str(site_data_with_data_limit))
	if total_text_length > MAX_TEXT_LENGTH:
		print(f"Total text length {total_text_length} exceeds the limit of {MAX_TEXT_LENGTH}. Truncating data. Use less max_depth to avoid truncation.")
		# Reversing the order by the longest link first because longest link info could contain less broad information
		for url, text in sorted(site_data_with_data_limit.items(), key=lambda x: len(x[1]), reverse=True):
			if total_text_length <= MAX_TEXT_LENGTH:
				break
			del site_data_with_data_limit[url]
			total_text_length -= len(text)

	return site_data_with_data_limit