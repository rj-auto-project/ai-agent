from langchain_google_genai import ChatGoogleGenerativeAI
import os
import sys
import asyncio
from pydantic import SecretStr
from dotenv import load_dotenv
import time

# Ensure the current directory is in sys.path to find custom_browser_use
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from custom_browser_use import Browser, Agent
except ImportError as e:
    print(f"Error: Could not import custom_browser_use: {e}")
    print("Ensure custom_browser_use.py or custom_browser_use/ is in the same directory as this script.")
    sys.exit(1)

# Load .env from the parent directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

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

# Improved agent with better instructions and error handling
async def main():
    agent = Agent(
        task=f"""
        1. Navigate to https://sso.rajasthan.gov.in/signin?encq=m0ZUFHLqc4t+0vQu27K7jl5cOBbodS7JFafFdflRFZs=.
        2. Perform the login process with these steps:
            ◦ Enter SSOID: '{ssoid}' in the SSOID field.
            ◦ Enter password: '{password}' in the password field.
            ◦ Fill the captcha field (read and enter the visible captcha text).
            ◦ If captcha fails (e.g., login error indicating incorrect captcha):
                - Refresh the entire page and restart login from step 2.
            ◦ If prompted "another session is active":
                - first, Enter the password '{password}'.
                - second, Check the confirmation checkbox.
                - Do NOT re-enter captcha unless explicitly required.
                - third, Click the login button.
            ◦ If prompted for a PIN, enter '{pin}' and submit.
            ◦ Wait up to 30 seconds for the Dashboard to load fully. If it doesn't load, refresh the webpage and retry login up to 3 times.
        3. Once on the Dashboard:
            ◦ Wait for the page to fully load (up to 30 seconds).
            ◦ Locate and click 'Load Dta' ONLY in the E-File section in dashboard (not in the navigation panel).
        4. In the E-File block:
            ◦ Find any blue-colored number (e.g., 1, 2, 10) below the E-File sub-heading in dashboard (ignore the calendar on the right).
            ◦ Click the number. If it doesn't navigate to the next page, retry clicking up to 5 times with a 2-second delay between attempts.
        5. On the new table page:
            ◦ Locate the blue-colored file number under the "File Number" column.
            ◦ Click it to open the file details.
        6. On the file details page:
            ◦ Hover over the "More" button in the top blue section, right of 'View Movement'.
            ◦ Click "Dispose" from the dropdown.
            ◦ In the popup, replace the "Dispose Remark Reason" text (default 'File Purpose is disposed') with '-'.
            ◦ Click "Dispose File" to submit.
        7. After disposing a file:
            ◦ Return to the E-File table (step 4) and repeat steps 5-6 for the next file.
            ◦ Continue until no blue-colored numbers remain in the E-File table.
        8. Error Handling:
            ◦ If any step fails (e.g., element not found, page not loading), wait 5 seconds and retry up to 3 times before moving to the next step or file.
            ◦ If login fails completely after 5 attempts, stop and report failure.
        """,
        llm=llm,
        max_failures=15,  # Increased to allow more retries
        browser=browser,
    )
    
    # Run the agent with a timeout for the entire process
    try:
        await asyncio.wait_for(agent.run(), timeout=3600)  # 1-hour timeout for the whole task
    except asyncio.TimeoutError:
        print("Process timed out after 1 hour.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())