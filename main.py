from langchain_google_genai import ChatGoogleGenerativeAI
import os
import sys
import asyncio
from pydantic import SecretStr,BaseModel
from dotenv import load_dotenv
from typing import Optional

try:
    from custom_browser_use import Browser, Agent,Controller
except ImportError as e:
    print(f"Error: Could not import custom_browser_use: {e}")
    print("Ensure custom_browser_use.py or custom_browser_use/ is in the same directory as this script.")
    sys.exit(1)

from custom_browser_use.agent.views import ActionResult

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from custom_browser_use.browser.browser import Browser, BrowserConfig
from custom_browser_use.browser.context import BrowserContext

class HoverAction(BaseModel):
	index: 	  Optional[int] = None
	xpath: 	  Optional[str] = None
	selector: Optional[str] = None


# Ensure the current directory is in sys.path to find custom_browser_use
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)


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
browser = Browser(config=BrowserConfig(
        headless=False,
    ))


controller = Controller()

@controller.registry.action(
    'Hover over an element',
    param_model=HoverAction,  # Define this model with at least "index: int" field
)
async def hover_element(params: HoverAction, browser: BrowserContext):
    """
    Hovers over the element specified by its index from the cached selector map or by XPath.
    """
    session = await browser.get_session()
    state = session.cached_state

    if params.xpath:
        # Use XPath to locate the element
        element_handle = await browser.get_locate_element_by_xpath(params.xpath)
        if element_handle is None:
            raise Exception(f'Failed to locate element with XPath {params.xpath}')
    elif params.selector:
        # Use CSS selector to locate the element
        element_handle = await browser.get_locate_element_by_css_selector(params.selector)
        if element_handle is None:
            raise Exception(f'Failed to locate element with CSS Selector {params.selector}')
    elif params.index is not None:
        # Use index to locate the element
        if state is None or params.index not in state.selector_map:
            raise Exception(f'Element index {params.index} does not exist - retry or use alternative actions')
        element_node = state.selector_map[params.index]
        element_handle = await browser.get_locate_element(element_node)
        if element_handle is None:
            raise Exception(f'Failed to locate element with index {params.index}')
    else:
        raise Exception('Either index or xpath must be provided')

    try:
        await element_handle.hover()
        msg = f'🖱️ Hovered over element at index {params.index}' if params.index is not None else f'🖱️ Hovered over element with XPath {params.xpath}'
        return ActionResult(extracted_content=msg, include_in_memory=True)
    except Exception as e:
        err_msg = f'❌ Failed to hover over element: {str(e)}'
        raise Exception(err_msg)

# Improved agent with updated prompt
async def main():
    max_retries = 10
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            agent = Agent(
                task=f"""
                ***Must follow the tasks in order as written.***

                1. **Navigate to the login page**:
                        - Go to https://sso.rajasthan.gov.in/signin?encq=m0ZUFHLqc4t+0vQu27K7jl5cOBbodS7JFafFdflRFZs=.
                    if site not reached or failed:
                        - refresh the page and retry.

                2. **Perform the login process**:
                    a. Enter SSOID: '{ssoid}' in the SSOID field.
                    b. Enter password: '{password}' in the password field.
                    c. Fill the captcha field by reading and entering the visible captcha text.
                    d. Click the login button.
                    e. **Handle login conditions**:
                        - If captcha fails (e.g., error indicating incorrect captcha):
                            - Refresh the entire page and restart login from step 2.
                        - If prompted like "another session is active":
                            1. enter SSOID if not already entered else leave.
                            1. Check the confirmation checkbox.
                            2. Enter the password '{password}' in the password field.
                            3. Do NOT re-enter captcha unless explicitly required.
                            4. check if password is entered and checkbox is checked:
                                if yes:
                                    Click the login button.
                                else:
                                    do the task and then click on login button.
                        - If prompted for a PIN:
                            - Enter '{pin}' and submit.
                    f. Wait up to 30 seconds for the Dashboard to load fully. If it doesn't load, refresh the page and retry login up to 3 times.

                3. **Once on the Dashboard**:
                    a. check if the dashboard is loaded.
                    b. click on the element with xpath //div[contains(text(), 'E-File')])[1]
                        -if element not found:
                            -click on the E-file button under Inbox section on navigation panel.
                        else:
                            -refresh the page and retry.

                4. **Table will load on the dashboard (wait fot the table to load wth heading Inbox)**:
                    a. click on the number of first file under 'File No.' column in the table.
                    b. file details page will open. If not, try to click again, its a blue colored text under file no. coloumn of the table.

                5. **On the file details page**:
                    a. Hover the element with the xpath //div/button[contains(text(), 'More')], then click on element with xpath //a[contains(text(), 'Dispose')].
                        -if not found:
                            -hover over the element with text "More", then click on the " Dispose" button under it.
                    b. Wait for the popup,
                        -if popup not loaded:
                            -redo the step a.
                    c. In the popup, replace the "Dispose Remark Reason" text (default 'File Purpose is disposed') with '-'.
                    d. Click "Dispose File" to submit.

                6. **After disposing a file**:
                    a. Repeat step 4 and step 5, to dispose the all the file similarly.
                    b. check if all the files are disposed, if not keep disposing the files.

                7. **Error Handling**:
                    a. If any step fails (e.g., element not found, page not loading), wait 5 seconds and refresh the page then start from the step where it is needed like is asks for login do the login process ot if in home page then go to e-file and take other steps.
                    b. If login fails completely after 5 attempts, stop and report failure.
                """,
                llm=llm,
                max_failures=15,
                browser=browser,
                controller=controller,
            )
            
            await asyncio.wait_for(agent.run(), timeout=3600)  # 1-hour timeout
            print("Process completed successfully.")
        
            retry_count += 1
            
        except asyncio.TimeoutError:
            print(f"Process timed out after 1 hour. Attempt {retry_count + 1} of {max_retries}")
            retry_count += 1
            if retry_count < max_retries:
                print("Retrying in 30 seconds...")
                await asyncio.sleep(30)
                
        except Exception as e:
            print(f"An error occurred: {e}. Attempt {retry_count + 1} of {max_retries}")
            retry_count += 1
            if retry_count < max_retries:
                print("Retrying in 30 seconds...")
                await asyncio.sleep(30)
    
    if retry_count >= max_retries:
        print("Maximum retry attempts reached. Process failed.")

if __name__ == "__main__":
    asyncio.run(main())