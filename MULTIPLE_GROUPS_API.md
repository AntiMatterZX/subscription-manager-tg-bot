# Multiple Groups Per Product - API Changes

## Updated Endpoints

### Products API

#### List Product Groups
- `GET /api/products/{product_id}/groups` - List all Telegram groups mapped to a product

#### Map Product to Group (unchanged)
- `POST /api/products/{product_id}/map` - Map a product to a Telegram group
  - Body: `{"telegram_group_id": "string", "telegram_group_name": "string"}`
  - Now supports mapping multiple groups to the same product

#### Unmap Product from Groups (updated)
- `DELETE /api/products/{product_id}/unmap` - Unmap product from Telegram groups
  - Body (optional): `{"telegram_group_id": "string"}` - Unmap specific group
  - Body (empty): Unmap all groups from product

### Subscription Behavior

When creating subscriptions for products with multiple groups:
- System automatically selects the first **active** group
- If no active groups exist, subscription creation fails
- Existing subscriptions continue to work with their assigned group

### Database Changes

- Removed unique constraint on `telegram_groups.product_id`
- Products can now have multiple `telegram_groups`
- Backward compatible with existing single-group mappings

### Migration

Run the database migration to remove the unique constraint:
```bash
flask db upgrade
```

## Example Usage

```bash
# Map multiple groups to one product
POST /api/products/pro-basic/map
{"telegram_group_id": "-1001234567890", "telegram_group_name": "VIP Group 1"}

POST /api/products/pro-basic/map  
{"telegram_group_id": "-1001234567891", "telegram_group_name": "VIP Group 2"}

# List all groups for a product
GET /api/products/pro-basic/groups

# Unmap specific group
DELETE /api/products/pro-basic/unmap
{"telegram_group_id": "-1001234567890"}

# Unmap all groups
DELETE /api/products/pro-basic/unmap
```