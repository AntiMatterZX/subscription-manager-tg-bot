from marshmallow import Schema, fields, validate


class ProductSchema(Schema):
    id = fields.Str(required=True, validate=validate.Length(min=1, max=24))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

    # Include telegram_group information if available
    telegram_group = fields.Nested(
        "TelegramGroupSchema", exclude=("product",), dump_only=True
    )


class ProductCreateSchema(Schema):
    id = fields.Str(required=True, validate=validate.Length(min=1, max=24))
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)


class ProductUpdateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(allow_none=True)


product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
product_create_schema = ProductCreateSchema()
product_update_schema = ProductUpdateSchema()
