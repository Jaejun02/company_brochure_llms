# Project: Company Brochure Using LLMs

## Project Starting Guide
1. Open up `company_brochure_llm` file on your editor (e.g., VS Code, Jupyter Lab etc.). Note that your working directory should be inside `company_brochure_llm` file, on the same level as `src` file.
2. Use `conda env create -f environment.yml` to create an virtual environment. ([Anaconda](https://www.anaconda.com/download/success) has to be pre-installed for this to work.)
3. Create your own **.env**, and include your Open AI's API key as `OPENAI_API_KEY=your_api_key_goes_here`. Note: Having any spaces next to the equation symbol would cause an error.
4. Download [Ollama](https://ollama.com/download).
5. Open your terminal, and type `ollama pull qwen2.5`. Make sure that all of its models are downloaded. Note: if you would not want to download a local LLM or if your local PC cannot support the LLM, you can skip 3~4.
6. Now, you can run the `company_brochure.py`. Note: you need to set the Company Brochure Language to 'English' if you have not downloaded **qwen2.5** model. 
