def classifier(URL: str) -> str:
    prompt = f'''
    Categorize this company in 2 words: {URL}
    Response nothing but in this format: Company - Category
    '''
    print('Your prompt is: ', prompt)
    
    
if __name__ == '__main__':
    classifier('https://www.google.com')