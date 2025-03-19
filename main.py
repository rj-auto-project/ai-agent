from langchain_google_genai import ChatGoogleGenerativeAI
# from browser_use import Agent, Browser
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
    3. Wait for the Dashboard to load completely.
    4. Locate and click on 'Load Data' (Only in the E-File section within the dashboard, NOT in the navigation panel).
    5. Find the number under the "E-File" section (it can be any number, not just '1').
        • Ensure it is inside the "E-File" section, NOT the calendar on the right. 
        • Click on the blue-colored number (e.g., 1, 2, 10, etc.) inside the E-File table only. 
        • If clicking does not navigate to the next page, retry clicking until it moves forward.
    6. Once the new table opens:
        ◦ Find the blue-colored file number under the "File Number" column. 
        ◦ Click on the file number to open its details. 
    7. In the newly opened page:
        ◦ Hover over the "More" button on the top blue section on the right side of 'View Movement' option. 
        ◦ Click on the "Dispose" button.
        ◦ When a popup appears, click on "Dispose File" to finalize. 
    8. When disposed, get to the next file to dispose it as well.
    9. use step 6 and 7 to dispose other files as well
    9. keep disposing untill all the files are not disposed.
            """
        ),
        llm=llm,
        max_failures= 10,
        browser=browser,
    )
    await agent.run()
asyncio.run(main())
