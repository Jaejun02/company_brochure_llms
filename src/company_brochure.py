# imports
import os
import requests
import json
from typing import List
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from IPython.display import Markdown, display, update_display
from openai import OpenAI
import gradio as gr
import ollama

# initialize and constants
load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')
MODEL = 'gpt-4o-mini'
OLLAMA_MODEL = 'qwen2.5'
openai = OpenAI()

# A class to represent a Webpage

# Some websites need you to use proper headers when fetching them:
headers = {
 "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}

class Website:
    """
    A utility class to represent a Website that we have scraped, with links
    """

    def __init__(self, url):
        self.url = url
        response = requests.get(url, headers=headers)
        self.body = response.content
        soup = BeautifulSoup(self.body, 'html.parser')
        self.title = soup.title.string if soup.title else "No title found"
        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            self.text = soup.body.get_text(separator="\n", strip=True)
        else:
            self.text = ""
        links = [link.get('href') for link in soup.find_all('a')] 
        self.links = [link for link in links if link] 

    def get_contents(self):
        return f"Webpage Title:\n{self.title}\nWebpage Contents:\n{self.text}\n\n"
    
# Step 1: Have GPT-4o-mini to extract relevant links from our list of links
# Apply one-shot prompting.
link_system_prompt = "You are provided with a list of links found on a webpage. \
You are able to decide which of the links would be most relevant to include in a brochure about the company, \
such as links to an About page, or a Company page, or Careers/Jobs pages.\n"
link_system_prompt += "You should respond in JSON as in this example:"
link_system_prompt += """
{
    "links": [
        {"type": "about page", "url": "https://full.url/goes/here/about"},
        {"type": "careers page": "url": "https://another.full.url/careers"}
    ]
}
"""
def get_links_user_prompt(website):
    user_prompt = f"Here is the list of links on the website of {website.url} - "
    user_prompt += "please decide which of these are relevant web links for a brochure about the company, respond with the full https URL in JSON format. \
Do not include Terms of Service, Privacy, email links.\n"
    user_prompt += "Links (some might be relative links):\n"
    user_prompt += "\n".join(website.links)
    return user_prompt
def get_links(url):
    website = Website(url)
    response = openai.chat.completions.create( 
        model=MODEL,
        messages=[
            {"role": "system", "content": link_system_prompt},
            {"role": "user", "content": get_links_user_prompt(website)}
      ],
        response_format={"type": "json_object"} 
    )
    result = response.choices[0].message.content 
    return json.loads(result)

# Step 2: Create a Brochure out of all scraped links
system_prompt = "You are an assistant that analyzes the contents of several relevant pages from a company website \
and creates a short brochure about the company for prospective customers, investors and recruits. Respond in markdown.\
Include details of company culture, customers and careers/jobs if you have the information."
def gather_details(url):
    result = "Landing page:\n"
    result += Website(url).get_contents()
    links = get_links(url)
    for link in links["links"]:
        result += f"\n\n{link['type']}\n"
        result += Website(link["url"]).get_contents()
    return result
def get_brochure_user_prompt(company_name, url):
    user_prompt = f"You are looking at a company called: {company_name}\n"
    user_prompt += f"Here are the contents of its landing page and other relevant pages; use this information to build a short brochure of the company in markdown.\n"
    user_prompt += gather_details(url)
    user_prompt = user_prompt[:20_000] # Truncate if more than 20,000 characters
    return user_prompt
def create_brochure(company_name, url):
    response = openai.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": get_brochure_user_prompt(company_name, url)}
          ]
    )
    return response.choices[0].message.content

# Step 3: Use Local Ollama Model (qwen2.5) for Translation - Testing But not Recommended as Qwen 2.5 is somewhat not that fluent
translate_system_prompt = 'You are an assistant that translates a company brochure that is in English and given in Markdown format.\
 Translate the brochure to the language that is given in the user prompt. Respond in Markdown.'
    
def translate_brochure(company_name, url, language):
    brochure_content = create_brochure(company_name, url)
    if language == "English":
        return brochure_content
    user_prompt = f'Translate the given brochure content to {language}.\n\nBrochure Content: {brochure_content}.'
    messages = [{'role':'system', 'content':translate_system_prompt},
               {'role':'user', 'content': user_prompt}]
    response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
    return (response['message']['content'])

# Create a Simple User Interface with Gradio (HuggingFace's)
languages = ['Chinese', 'English', 'French', 'Spanish', 'Portugese', 'German', 'Italian', 'Russian', 'Japanese', 'Korean', 'Vietnamese', 'Thai', 'Arabic']
view = gr.Interface(
    fn=translate_brochure,
    inputs=[
        gr.Textbox(label="Company name:"),
        gr.Textbox(label="Landing page URL including http:// or https://"),
        gr.Dropdown(label='Supported Languages (English is Highly Preferred):', choices = languages, value='English')],
    outputs=[gr.Markdown(label="Brochure:")],
    flagging_mode="never"
)
view.launch(inbrowser=True)