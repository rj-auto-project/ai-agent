from langchain_google_genai import ChatGoogleGenerativeAI
from custom_browser_use import Agent, Browser
from pydantic import SecretStr
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(os.getenv('GEMINI_API_KEY')))
browser = Browser()
# Create agent with the model
async def main():
    agent = Agent(
        task=(
            """
    1. Go to https://sso.rajasthan.gov.in/signin?encq=m0ZUFHLqc4t+0vQu27K7jl5cOBbodS7JFafFdflRFZs=.
    2. Complete the login process:
        ◦ Enter username: 'ashokmeena88.doit' 
        ◦ Enter password: 'A4Ashok##' 
        ◦ Enter captcha (ensure it's filled before clicking login). 
        ◦ If captcha is incorrect → Refresh the page and retry login. 
        ◦ If another session is active, enter the password again, check the confirmation checkbox, but do not enter captcha. Click login. 
        ◦ If prompted for a PIN, enter '112233' to proceed. 
            """
        ),
        llm=llm,
        max_failures= 5,
        browser=browser,
    )
    await agent.run()
asyncio.run(main())




# from langchain_openai import ChatOpenAI
# from custom_browser_use import Agent
# import asyncio
# from dotenv import load_dotenv
# load_dotenv()

# async def main():
#     agent = Agent(
#                 task=(
    #         """
    # 1. Go to https://sso.rajasthan.gov.in/signin?encq=m0ZUFHLqc4t+0vQu27K7jl5cOBbodS7JFafFdflRFZs=.
    # 2. Complete the login process:
    #     ◦ Enter username: 'ashokmeena88.doit' 
    #     ◦ Enter password: 'A4Ashok##' 
    #     ◦ Enter captcha (ensure it's filled before clicking login). 
    #     ◦ If captcha is incorrect → Refresh the page and retry login. 
    #     ◦ If another session is active, enter the password again, check the confirmation checkbox, but do not enter captcha. Click login. 
    #     ◦ If prompted for a PIN, enter '112233' to proceed. 
    # 3. Wait for the Dashboard to load completely.
    # 4. Locate and click on 'Load Data' (Only in the E-File section within the dashboard, NOT in the navigation panel).
    # 5. Find the number under the "E-File" section (it can be any number, not just '1').
    #     • Ensure it is inside the "E-File" section, NOT the calendar on the right. 
    #     • Click on the blue-colored number (e.g., 1, 2, 10, etc.) inside the E-File table only. 
    #     • If clicking does not navigate to the next page, retry clicking until it moves forward.
    # 6. Once the new table opens:
    #     ◦ Find the blue-colored file number under the "File Number" column. 
    #     ◦ Click on the file number to open its details. 
    # 7. In the newly opened page:
    #     ◦ Hover over the "More Options" button at the top of the page. 
    #     ◦ Click on the "Dispose" button. 
    #     ◦ When a popup appears, click on "Dispose File" to finalize. 
    # 8. Console Output: Print the number of files found under the E-File section.
    #         """
#         ),
#         llm=ChatOpenAI(model="gpt-4o"),
#     )
#     await agent.run()

# asyncio.run(main())