# AI Prompt Log

## 2026-10-05

> Please create AI_prompts.md as a log of what I type into the vibe coder. Log my words and execute the written request in the same go.

## LOG MAINTENANCE

> You're getting creative with the order of the entries in AI_prompts. It really should be sequential

## PROBLEM 2: ANALYZE THE DATABASE

> Please gain an understanding of the data in data/campus_customs.db, with a focus on catalogue, inventory, and users. Once done, create the file output/harness.md. Write down each table and its fields, and one short line on why each field matters for the shop or the chatbot. We will keep growing this harness file as we keep working.

## PROBLEM 3: BUILD THE CAMPUS CUSTOMS WEBSITE

> Scaffold a React + Vite + TypeScript front end for Campus Customs. Put a nav bar at the top that links to the main pages: Home, Products, About Us, Log In, Create Account.
>
> Pull Campus Customs-style wording from yalebulldogblue.com for Home and About Us, but write these pages in your own voice, inspired by a peppy school-spirited student.
>
> On the Products page, show product images using the catalogue. You can use image paths provided in the database. Also show product info (include name, price, short description). Clicking on a card on this page should take shoppers to individual pages.
>
> Build those individual pages. Those individual product pages should include a large image on the left side, full product text on the right including first price, prominently featured, size/stock when you have them next, finally description.
>
> Add a chat interface on the bottom right of the site (a floating chat panel that can be minimized). It does not need to be able to talk yet. We'll build that later. For now, a stub that will call the backend later is enough for Problem 3.
>
> You will need a small API soon to read the database. It is fine to start a simple FastAPI app in backend/main.py just to serve products and images. We'll grow it into an agent backend in Problem 5.

## PROBLEM 4: CREATE ACCOUNT AND LOGIN

> Build a create-account / login flow. Create account should ask for first name, last name, email, password, confirm password. Require password includes a lower and uppercase letter and a number and is at least 6 characters. Add an optional phone number field.
>
> Log in should ask for email and password, and have a button for "Forgot your password?" It should navigate to another page that simply says "Aww man :("

> New accounts should go into the users table. Make sure passwords are stored securely, safe against both humans and AI accessing. The seed database already has a test user you can use while building. Email test@campuscustoms.yale.edu and password: password. Update output/harness.md with how authorization works (what you store for a user and how passwords are protected).

> For confirm password under create account, add a response that either in green text says Passwords match! or in red text says Passwords do not match :(

> Password criteria (lower, upper, number, 6 characters) should also be included as small text next to the password heading. Add a response that either in green text says Criteria met! or in red text says Criteria not met :(

> Unless both green texts are displayed, keep the Create Account button grayed out and nonresponsive.

> Once an account is created, show a popup window that says Your Account was Successfully Created! before the page refreshes to the home.

> The log in page should just have a standard password box without the bells and whistles.

> Once logged in, replace Log In with something like Hello <first name>.

> Next to Hello first name, add a functional Log Out.

## PROBLEM 5: PYDANTICAI AGENT BACKEND

> Build the shop chatbot as a PydanticAI agent behind FastAPI, plugged into our front end chat widget. Put the API app in backend/main.py. Keep the agent as these four files next to it: backend/prompts/prompt.md (system prompt that will grow as a file later), backend/agent.py (agent entry/wiring), backend/tools.py (tools the agent can call), backend/models.py (pydantic/pydanticAI structured types).
>
> In main.py expose a chat route so a message from the website returns a reply from the agent (and whatever else you need for products/auth). Use my AI model API key for the agent. Keep it cheap though! And say so in harness.md.
>
> Put Campus Customs voice and safety basics into prompts/prompt.md (we'll expand this later). Start or update types in models.py for chat replies/product cards as needed.
>
> In output/harness.md, note how the front end talks to FastAPI and how the agent is loaded (prompt file + model). Make sure the backend runs from the backend/ folder like this: uvicorn main:app --reload --port 8000.

## WORKFLOW CHECK

> Do you remember the workflow from earlier today? Updating AI_prompts.md with my typed inputs?

## PROBLEM 6: TOOLS: PRODUCT INFO AND STOCK

> Give the chat widget agent tools that look up real information from campus_customs.db including product description, price, how many of each item are in stock (by size when the customer asks). The agent must use the database, do not invent prices or quantities. Be honest if a size is out of stock and say so clearly.
>
> Expand prompts/prompt.md so the agent knows to call these tools for price and stock questions. Add or update return types in models.py. In output/harness.md, list each tool and explain which model fields you chose for lookup results and why.

## PROBLEM 7: CHAT SEARCH THAT UPDATES THE PAGE

> When a customer asks about a type of item, for example "what kind of hoodies do you have," the agent should search the catalogue and the website should dynamically show those matching items as product cards (image, name, price, short info). This should be an API contract: the agent returns structured product matches and then the front end renders them on the website.
>
> After the dynamic product cards are loaded by your new feature, make sure the same single-item page behavior built in Problem 3 still works: each product card, including the ones the chat just put on the page, should still open their respective pages when clicked.
>
> Update prompts/prompt.md and output/harness.md so it is clear how search results reach teh page.

> When you say "The frontend chat panel still needs the final rendering hookup so those returned cards visibly appear in the widget." how do we create that hookup

> Could you do this?

> On the main product page, can you also add a Sort by: with a dropdown that offers options name (A to Z), price (lowest to highest), price (highest to lowest) that respondscorrectly when clicked

> That mostly worked. The chat widget needs some adjustments. 1. what the customer types needs to stay in the chat history as a bubble up top. the chat area needs to be able to scroll to contain text and the new card elements

> Maybe the description field on the dynamic card should only show two lines of text before trailing off with ...

> Also if a customer gives a broad search, the agent should (1) ask for more defining info first to narrow the potential products down then, (2) only offer 3 options in one reply. The agent can say "If you'd like to see more options, let me know!" only if it actually has more than 3 options, then if the user responds in affirmative produces the next two and ends there.

> Do you see in this chat interaction, the agent forgot I was talking about a tshirt? Can we have it remember a reasonable amount of messages back in the chat history? Maybe like 5 user inputs.

> here's more dialogue "Here are the three most relevant catalogue matches I found. Prices and availability come directly from our database. If you'd like to see more options, let me know! ... I had to clarify i wanted more products shown. the agent has to be more ready to respond to customers

> Can the pop up window also just be taller by 10%

> make it an even 450 px

> make it 600 px please

> can we make it 1000px tall?

> make it 5000 px tall

> oh my goodness, well set the max height at like 800 and make the actual on screen height 500

> make it max 500 and visibly 300

> match the max and the actual height at 300

> make it 250

> "If you'd like to see more options, let me know!" is not working bc typed responses have too much variability. Instead of the text, IF more options are available, have a message appear at the bottom of the chat that says "Show more?" and a "yes" "no" button that responds accordingly. If "yes" show two more products max. If "no" the chat should ask if there's anything else it can help with

> the show more sequence should only fire after three product cards have been shown

> The yes/no buttons are not responsive to clicks

> When i asked for a hoodie, it said "Absolutely! Are you looking for a pullover or full-zip hoodieâ€”and do you have a preferred size or budget? Here are three popular options to start:" and gave me three cards. I need to clarify the agents process. Yes it should continue asking for better details, then WAIT for the customers response before showing three best fits, only if more than one is needed

## PROBLEM 8: CUSTOMER MEMORY

> When a shopper is logged in, save their chat history in the database in an appropriate table and reload it when they return. The agent should know who is chatting (by name and email) and can even use the first name in the chat when appropriate "Hi first name! Thanks for having an account." at the start can be nice. Put that in agent deps (or an equivalent clear pattern) and /or tools the agent can call.
>
> Also pass enough page context that if someone is on a product page and asks a question like "do you have this in pink" the agent knows "this" is talking about the product from the page the customer is on. You can put code into the agent context.
>
> Guests can still chat, but history only needs to persist for logged-in users (but keep the rules we built in the previous problem about logging 5 messages from the user chat history as the guest rules). Document in output/harness.md how user chat history is stored, what customer fields the agnet sees, and how page context is passed.

## PROBLEM 9: USABILITY IMPROVEMENTS

> The assignment asks us to implement 2 front end usability improvements and 2 agent backend usability improvements. Front end usability improvements are being defined as improvements that make the site look better and make it easier to use while agent/backend improvements are defined as things that make the agent ouptut better, more accurate, or safer. These could be new agent tools or things that make the agent run faster or cheaper. I feel like we've done this already. What do you think?

> front end number one should only be product search, pagination, and sorting by name/price as three different items. a fourth item can be the "hi first name" after log in. a fifth is scrollable chat history. I'm including these guys but excluding product readable bubbles, product cards, and clickable product links because those were assignment requirements.

> please write these improvements and why each helps Campus Customs shoppers or the business as a file output/usability.md

> Update this md if we keep adding cool front and backend features.
>
> for example, a backend feature should include a safety feature of not storing sensitive information. for instance if the logged in user shares a credit card number or password in the chat

## PROBLEM 10: STYLE THE WEBSITE

> Add creative design so the site feels like a real Campus Customs storefront--fonts, color, hierarchy, motion, product presentation, chat feel. I feel like we've done most of this. Any reccomendations? Please wait for permission before implementing

> Let's implement 1, 2, and 6. Write output/design.md that shares what we changed and why it helps with customer retention and conversion. Keep it short and sweet.

> Can you make this guy pop up from the bottom of the page like 2 seconds after a page loads? after being static and visible for 4 seconds, he should then descend out of sight into the bottom of the window

> [Uploaded the Yale-sweater bulldog image and saved it as public/bulldog-mascot.png.]

> make sure you log this in output/design.md

> 1) i want him to slide up on each new page navigated to. 2) reduce the waiting time from 2 seconds to 1.3 seconds. 3) he should slide up from the bottom rather than appear immediately 4) he can slide up from a different place along the bottom each time

> the bulldog (dan) appears instantly, rather than sliding up from the bottom. why is that?

> can dan bypass that?

> he's still appearing instantly

> looks great

## PROBLEM 11: SITE TESTING (APP CHECK)

> PROBLEM 11: SITE TESTING (APP CHECK) asks we test the live site and document it in output/app_check.html (a page one can double-click to open). I'll include screenshots depicting the three required scenarios:
>
> 1. chat checking the inventory level of an item (honest stock/price from the DB)
> 2. the dynamic search-result cards appearing after a category question
> 3. one of the usability features we added in problem 9.
>
> when i provide those, please add those to the site along with captions.
>
> Make the HTML easy to grade. Heading for each check, screenshot, one or two sentences on what the screenshot proves. I'll add the screenshots to ouptut/app_check_images/. please maek the folder and link them from app_check.html with relative paths (for example app_check_images/inventory.png)

> Hey at some point we lost the chat widget, add that back in.

> images are uploaded for proble 11

## PROBLEM 12: AUDIT TRAIL, SAFETY, FINISH HARNESS

> For PROBLEM 12: AUDIT TRAIL, SAFETY, FINISH HARNESS keep an append-only ouptut/audit_trail.json of agent-loop activity (time, tool name, short args/result, stop reason). Do not wipe it between runs. Also think of some additional safety rules to give the agent. Suggest them to me, wait to implement til I approve, then put them in prompts/prompt.md once implemented.
>
> Finish output/harness.md so it is clear how the system works: model fields in models.py and why you chose them, tools and abilities, safety rules, specs (loop limits, result caps, models, how to run front + back)

> implement all 5

> For dan's animation, make sure he never overlaps with the chat window while keeping the randomization of where he appears from

> logging out should refresh the page

> This didn't work well. Hi Gavin! Medium isn’t listed in the inventory for the 2025 Yale v Harvard T-Shirt, so I can’t confirm a quantity for that size. try again I retried it, Gavin—the 2025 Yale vs Harvard T-Shirt is listed with 20 in stock in medium (M).

> this also was a failure: hi, how many of the yale v harvard t shirt are in stock in medium? I couldn’t find a Medium size listing for the Yale v Harvard T-Shirt, so I can’t confirm any Medium stock. Want me to look for the shirt under a slightly different product name?




