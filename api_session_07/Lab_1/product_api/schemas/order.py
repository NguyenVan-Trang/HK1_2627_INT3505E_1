from marshmallow import Schema, fields, validate


class OrderItemIn(Schema):
    product_id = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1)
    )

    qty = fields.Int(
        required=True,
        strict=True,
        validate=validate.Range(min=1)
    )


class OrderCreate(Schema):
    items = fields.List(
        fields.Nested(OrderItemIn),
        required=True,
        validate=validate.Length(min=1)
    )


class OrderItemOut(Schema):
    id = fields.Int(dump_only=True)
    product_id = fields.Int()
    qty = fields.Int()
    unit_price_cents = fields.Int()


class OrderOut(Schema):
    id = fields.Int()
    status = fields.Str()
    created_at = fields.DateTime()
    items = fields.Nested(OrderItemOut, many=True)