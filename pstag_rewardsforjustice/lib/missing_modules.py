import os

# PIP INSTALL REQUIRED MODULES AUTOMATICALLY

while True:
    try:
        import scrapy
        import selenium
        import scrapy_selenium
        from dotenv import load_dotenv
        # END TEST IMPORTS
        break
    except ModuleNotFoundError as e:
        os.system(f"pip install scrapy")
        os.system(f"pip install selenium")
        os.system(f"pip install python-dotenv")
        os.system(f"pip install scrapy-selenium")
        os.system(f"pip install scrapy-xlsx")

    
