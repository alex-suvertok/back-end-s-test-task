from modeltranslation.translator import translator, TranslationOptions
from .models import Unit, Attribute, AttributeValue, Category, Product


class UnitTranslationOptions(TranslationOptions):
    fields = ("title",)


translator.register(Unit, UnitTranslationOptions)


class AttributeTranslationOptions(TranslationOptions):
    fields = (
        "title",
        "help_text",
    )


translator.register(Attribute, AttributeTranslationOptions)


class AttributeValueTranslationOptions(TranslationOptions):
    fields = ("title",)


translator.register(AttributeValue, AttributeValueTranslationOptions)


class CategoryTranslationOptions(TranslationOptions):
    fields = (
        "image_alt",
        "title",
        "h1_title",
        "description",
        "banner_alt",
        "icon_alt",
    )


translator.register(Category, CategoryTranslationOptions)


class ProductTranslationOptions(TranslationOptions):
    fields = (
        "name",
        "description",
    )


translator.register(Product, ProductTranslationOptions)
