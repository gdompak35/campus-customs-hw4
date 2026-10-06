from pathlib import Path
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from pydantic_ai import Agent, RunContext, UsageLimits
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.exceptions import UsageLimitExceeded
import json
from datetime import datetime, timezone
try:
    from .models import ChatReply, ShopDeps, ProductCard, ProductInfo, StockLookup, CustomerContext
    from .tools import search_products, lookup_product, check_stock
except ImportError:
    from models import ChatReply, ShopDeps, ProductCard, ProductInfo, StockLookup, CustomerContext
    from tools import search_products, lookup_product, check_stock

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AUDIT_FILE = PROJECT_ROOT / 'output' / 'audit_trail.json'

def audit_event(tool_name: str, args=None, result=None, stop_reason=None):
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        entries = json.loads(AUDIT_FILE.read_text(encoding='utf-8')) if AUDIT_FILE.exists() else []
    except (OSError, json.JSONDecodeError):
        entries = []
    entries.append({'time': datetime.now(timezone.utc).isoformat(), 'tool_name': tool_name, 'args': str(args or '')[:240], 'result': str(result or '')[:240], 'stop_reason': stop_reason})
    AUDIT_FILE.write_text(json.dumps(entries, indent=2), encoding='utf-8')
load_dotenv(PROJECT_ROOT / '.env', override=True)
SYSTEM_PROMPT = (Path(__file__).resolve().parent / 'prompts' / 'prompt.md').read_text(encoding='utf-8')

portkey_key = os.getenv('PORTKEY_API_KEY')
if portkey_key:
    portkey_client = AsyncOpenAI(
        api_key=portkey_key,
        base_url='https://api.portkey.ai/v1',
        default_headers={'x-portkey-api-key': portkey_key, 'x-portkey-provider': 'openai'},
    )
    model = OpenAIChatModel('gpt-4o-mini', provider=OpenAIProvider(openai_client=portkey_client))
else:
    model = 'openai:gpt-4o-mini'

agent = Agent(model, deps_type=ShopDeps, output_type=ChatReply, system_prompt=SYSTEM_PROMPT)

@agent.tool
def find_products(ctx: RunContext[ShopDeps], search: str) -> list[ProductCard]:
    """Search the live Campus Customs catalogue and inventory."""
    result = search_products(search)
    audit_event('find_products', search, f'{len(result)} results')
    return result

@agent.tool
def get_product_info(ctx: RunContext[ShopDeps], product: str) -> ProductInfo | None:
    """Get database-backed description, price, colors, and size stock."""
    result = lookup_product(product)
    audit_event('get_product_info', product, 'found' if result else 'not found')
    return result

@agent.tool
def get_stock(ctx: RunContext[ShopDeps], product: str, size: str | None = None) -> StockLookup:
    """Get database-backed stock, optionally for one requested size."""
    result = check_stock(product, size)
    audit_event('get_stock', {'product': product, 'size': size}, result.model_dump(), 'complete')
    return result

async def run_agent(message: str, history: list[str] | None = None, customer: dict | None = None, page_context: str | None = None) -> ChatReply:
    audit_event('agent_loop', message, None, 'started')
    recent = (history or [])[-5:]
    size_names = {'xs':'XS','extra small':'XS','s':'S','small':'S','m':'M','medium':'M','l':'L','large':'L','xl':'XL','extra large':'XL','xxl':'XXL','2xl':'XXL'}
    lowered = message.lower()
    requested_size = next((value for key, value in size_names.items() if key in lowered), None)
    if requested_size and recent:
        prior_query = next((item for item in reversed(recent) if item.lower().strip() not in {'try again','retry','again'}), recent[-1])
        candidates = search_products(prior_query)
        if candidates:
            stock = check_stock(candidates[0].name, requested_size)
            if stock.found:
                if stock.results:
                    item = stock.results[0]
                    availability = f'{item.quantity} in stock' if item.quantity > 0 else 'out of stock'
            response = ChatReply(reply=f'{candidates[0].name} has {availability} in size {item.size}.', products=[candidates[0]])
            audit_event('agent_loop', message, response.reply, 'complete')
            return response
                response = ChatReply(reply=f'{requested_size} is not listed in the inventory for {candidates[0].name}, so I cannot confirm a quantity for that size.', products=[candidates[0]])
                audit_event('agent_loop', message, response.reply, 'complete')
                return response
    more_phrases = {'more', 'show me more', 'show more', 'yes', 'yes please', 'yes, please', 'sure', 'sure please'}
    asks_for_more = message.lower().strip() in more_phrases or 'show me more' in message.lower()
    if recent and message.lower().strip() in {'no', 'no thanks', 'no thank you'}:
            response = ChatReply(reply='No problem! Is there anything else I can help you with?')
            audit_event('agent_loop', message, response.reply, 'complete')
            return response
    if recent and asks_for_more:
        prior_query = next((item for item in reversed(recent) if item.lower().strip() not in more_phrases and 'show me more' not in item.lower()), recent[0])
        prior_matches = search_products(prior_query)
        additional = prior_matches[3:5]
        if additional:
            response = ChatReply(reply='Here are two more matches from that search.', products=additional, more_available=False)
            audit_event('agent_loop', message, response.reply, 'complete')
            return response
        response = ChatReply(reply='I did not find additional matches for that search.')
        audit_event('agent_loop', message, response.reply, 'complete')
        return response
    context = '\n'.join(f'Customer message {index + 1}: {text}' for index, text in enumerate(recent))
    identity = f"Shopper: {customer.get('first_name', '')} {customer.get('last_name', '')} ({customer.get('email', '')})" if customer else 'Shopper: guest'
    prompt = f'{identity}\nPage context: {page_context or "none"}\nConversation context from the last customer messages:\n{context}\n\nCurrent customer message: {message}' if context else f'{identity}\nPage context: {page_context or "none"}\nCurrent customer message: {message}'
    try:
        result = await agent.run(prompt, deps=ShopDeps(), usage_limits=UsageLimits(request_limit=8))
        output = result.output
        output.more_available = len(search_products(message)) > len(output.products)
        audit_event('agent_loop', message, output.reply, 'complete')
        return output
    except UsageLimitExceeded:
        audit_event('agent_loop', message, None, 'request_limit_exceeded')
        broad_terms = {'hoodie', 'hoodies', 't-shirt', 'tshirts', 't-shirt', 'shirt', 'shirts', 'crewneck', 'sweatshirt'}
        words = set(message.lower().replace(',', '').split())
        if not (history or []) and words & broad_terms and len(words) <= 6:
            return ChatReply(reply='What kind of item would you prefer—pullover or full-zip, and do you have a color, size, or budget in mind?')
        matches = search_products(message)
        if matches:
            extra = ' If you\'d like to see more options, let me know!' if len(matches) > 3 else ''
            return ChatReply(reply='Here are the three most relevant catalogue matches I found. Prices and availability come directly from our database.', products=matches[:3], more_available=len(matches) > 3)
        return ChatReply(reply='I could not find a matching catalogue item. Try a product type such as hoodie, crewneck, or T-shirt.')
