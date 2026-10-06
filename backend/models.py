from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    user_id: int | None = None
    history: list[str] = Field(default_factory=list, max_length=5)
    page_context: str | None = None

class ProductCard(BaseModel):
    product_id: str
    name: str
    price: float
    description: str
    image_url: str
    sizes: list['StockItem'] = []

class StockItem(BaseModel):
    size: str
    quantity: int
    in_stock: bool

class ProductInfo(BaseModel):
    product_id: str
    name: str
    garment_type: str
    description: str
    price: float
    colors: list[str] = []
    stock: list[StockItem] = []

class StockLookup(BaseModel):
    product_id: str
    product_name: str
    requested_size: str | None = None
    results: list[StockItem] = []
    found: bool

class ChatReply(BaseModel):
    reply: str
    products: list[ProductCard] = []
    more_available: bool = False

class ShopDeps: pass

class CustomerContext(BaseModel):
    user_id: int | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: str | None = None
    page_context: str | None = None

ProductCard.model_rebuild()
