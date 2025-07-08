import datetime
from agents import function_tool
from duckduckgo_search import DDGS


@function_tool()
def get_news_articles(topic: str):
    """
    Searches for recent news articles on a specific topic using DuckDuckGo.
    
    Args:
        topic (str): The topic or keywords to search for news articles
        
    Returns:
        str: Formatted news results with titles, URLs, and descriptions
    """
    print(f"Running DuckDuckGo news search for {topic}...")

    # Get the current date in YYYY-MM format
    current_date = datetime.datetime.now().strftime("%Y-%m")
    
    # DuckDuckGo search
    ddg_api = DDGS()
    results = ddg_api.text(f"{topic} {current_date}", max_results=5)
    if results:
        news_results = "\n\n".join([f"Title: {result['title']}\nURL: {result['href']}\nDescription: {result['body']}" for result in results])
        print(news_results)
        return news_results
    else:
        return f"Could not find news results for {topic}."