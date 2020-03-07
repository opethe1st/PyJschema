import unittest

from pyjschema.draft_2019_09 import validate


class TestRand(unittest.TestCase):
    def test(self):
        res = validate(
            schema={
                "$schema": "https://json-schema.org/draft/2019-09/schema",
                "$id": "http://example.com/product.schema.json",
                "title": "Product",
                "description": "A product from Acme's catalog",
                "type": "object",
                "properties": {
                    "productId": {"$ref": "http://example.com/product.schema.json#ID"},
                    "productName": {"type": "string"},
                    "price": {"type": "number"},
                    "tags": {
                        "$ref": "http://example.com/product.schema.json#ArrayOfStrings"
                    },
                },
                "required": ["productId"],
                "$defs": {
                    "ID": {
                        "$anchor": "ID",
                        "type": "integer",
                        "description": "The unique identifier for a product",
                    },
                    "ArrayOfStrings": {
                        "$anchor": "ArrayOfStrings",
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
            },
            instance={
                "productId": 1,
                "productName": "A green door",
                "price": 12.50,
                "tags": ["home", "green"],
            },
        )
        self.assertTrue(res)
