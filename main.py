from langchain_google_genai import ChatGoogleGenerativeAI
import os
import sys
import asyncio
from pydantic import SecretStr
from dotenv import load_dotenv

# Ensure the current directory is in sys.path to find custom_browser_use
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import custom_browser_use from the current directory
try:
    from custom_browser_use import Browser, Agent
except ImportError as e:
    print(f"Error: Could not import custom_browser_use: {e}")
    print("Ensure custom_browser_use.py or custom_browser_use/ is in the same directory as this script.")
    sys.exit(1)

# Load .env from the parent directory (since the Bash script creates it there)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

api_key = "AIzaSyCaRsppu7pV85-FvdjfcEsa5SKDQP-B880"
ssoid = os.getenv("SSOID")
password = os.getenv("PASSWORD")
pin = os.getenv("PIN")

if not all([api_key, ssoid, password, pin]):
    print("Error: Missing required environment variables in .env")
    sys.exit(1)

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key))
browser = Browser()

# Create agent with the model
async def main():
    agent = Agent(
        task=f"""
        1. Go to https://sso.rajasthan.gov.in/signin?encq=m0ZUFHLqc4t+0vQu27K7jl5cOBbodS7JFafFdflRFZs=.
        2. Complete the login process:
            ◦ Enter SSOID: '{ssoid}'
            ◦ Enter password: '{password}'
            ◦ Enter captcha (ensure it's filled before clicking login). 
            ◦ If captcha is incorrect → Refresh the page and retry login. 
            ◦ If another session is active, enter the password again, check the confirmation checkbox, but do not enter captcha. Click login. 
            ◦ If prompted for a PIN, enter '{pin}' to proceed. 
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
            ◦ When a popup appears, replace the text inside input field of "Dispose Remark Reason" i.e. 'File Purpose is disposed' with '-'.
            ◦ click on "Dispose File" to finalize. 
        8. When disposed, get to the next file to dispose it as well.
        9. Use step 6 and 7 to dispose other files as well
        9. Keep disposing until all the files are not disposed.
        """,
        llm=llm,
        max_failures=10,
        browser=browser,
    )
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())