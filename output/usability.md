# Campus Customs Usability Improvements

This document identifies the additional usability improvements implemented for Problem 9. Required assignment features such as product cards, readable chat bubbles, and clickable product links are not counted as improvements here.

## Frontend improvements

### 1. Product search

The Products page lets shoppers search the catalogue by product name, garment type, description, and search tags.

Why it helps: shoppers can quickly find relevant merchandise without browsing the entire catalogue. For Campus Customs, better discovery can increase product engagement and reduce the chance that customers leave without finding what they want.

### 2. Pagination

The Products page divides the catalogue into manageable pages and lets shoppers choose how many products to display.

Why it helps: shorter pages are easier to scan and less overwhelming, especially as the catalogue grows. It also keeps the interface responsive and gives the business room to add products without creating one unwieldy page.

### 3. Sorting by name and price

Shoppers can sort products by name from A to Z, price from lowest to highest, or price from highest to lowest.

Why it helps: sorting supports different shopping goals. A shopper can find a familiar item alphabetically, begin with an affordable option, or compare premium products. This makes the catalogue more useful for different budgets and shopping styles.

### 4. Personalized greeting after login

After login, the navigation changes to a greeting such as “Hi, Alex” and provides a visible logout action.

Why it helps: the greeting confirms that the account login worked and makes the store feel more welcoming. It also gives Campus Customs a simple foundation for personalized experiences while keeping account controls easy to find.

### 5. Scrollable chat history

The chat widget keeps the conversation in a scrollable panel so previous customer messages, assistant replies, and search results remain available without expanding the page indefinitely.

Why it helps: shoppers can review prior recommendations and follow-up questions without losing context. The fixed chat panel also keeps the rest of the storefront usable while supporting longer shopping conversations.

## Agent/backend improvements

### 1. Database-backed product and inventory tools

The agent uses tools that read product descriptions, prices, and size-level inventory from `campus_customs.db` instead of inventing catalogue facts.

Why it helps: shoppers receive trustworthy answers about what Campus Customs sells, what it costs, and which sizes are available. The business avoids misleading customers with fabricated prices or stock claims and can keep answers aligned with its current data.

### 2. Bounded context and structured, safe agent responses

The agent receives a bounded recent conversation context, uses structured product-card results, applies request limits, and receives customer/page context when available. Logged-in customer history is persisted separately and guests retain only the recent five-input behavior.

Why it helps: bounded context improves follow-up answers while controlling prompt size and model cost. Structured responses make product results predictable for the frontend, request limits reduce runaway calls, and customer/page context helps the agent answer questions such as “do you have this in pink?” more accurately without exposing passwords or other sensitive account data.

## Scope note

The list above separates Problem 9 improvements from baseline assignment requirements. The storefront’s product cards, chat cards, readable chat messages, and clickable product detail links remain important functionality, but they are not counted as the additional frontend usability improvements listed here.

## Ongoing feature additions

This document should be updated as new frontend and backend improvements are added. A further backend safety improvement now protects customer privacy in chat: likely credit-card numbers and explicit password disclosures are redacted before the message is sent to the agent or stored in `chat_messages`. The shopper receives a reminder not to share payment or password information, while the chat can continue using the non-sensitive portion of the message.
