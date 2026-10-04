"""Back-office forms for the catalog models.

ModelForms inherit the models' own rules (name required, slug unique);
the explicit ``price`` declaration adds the one rule the model doesn't
carry — the price must be positive. Widgets get their DaisyUI classes
in one shared ``__init__`` loop, as on ``CheckoutForm``.
"""

from decimal import Decimal

from django import forms
from django.core.files.uploadedfile import UploadedFile

from .models import Category, Product, Tag

# The largest photo staff may upload. Uploads are never resized, so this
# limit is the only guard on what the catalog serves.
MAX_IMAGE_MB = 2
MAX_IMAGE_BYTES = MAX_IMAGE_MB * 1024 * 1024


class StyledModelForm(forms.ModelForm):
    """Base form that dresses every widget in DaisyUI classes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = "toggle toggle-primary"
            elif isinstance(widget, forms.FileInput):
                widget.attrs["class"] = "file-input w-full"
            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = "textarea w-full"
                widget.attrs.setdefault("rows", 6)
            elif isinstance(widget, forms.SelectMultiple):
                widget.attrs["class"] = "select h-auto w-full"
                widget.attrs.setdefault("size", 8)
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = "select w-full"
            else:
                widget.attrs["class"] = "input w-full"


class ProductForm(StyledModelForm):
    price = forms.DecimalField(
        label="Price (USD)",
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
    )

    class Meta:
        model = Product
        fields = [
            "name",
            "slug",
            "tagline",
            "description",
            "price",
            "category",
            "tags",
            "is_available",
            "image",
        ]

    def clean_image(self):
        image = self.cleaned_data.get("image")
        # A cleared photo arrives as False and a kept one as the stored
        # file; only a fresh upload has a size worth checking.
        if isinstance(image, UploadedFile) and image.size > MAX_IMAGE_BYTES:
            raise forms.ValidationError(
                f"That file is too large. Photos can be at most {MAX_IMAGE_MB} MB."
            )
        return image


class CategoryForm(StyledModelForm):
    class Meta:
        model = Category
        fields = ["name", "slug"]


class TagForm(StyledModelForm):
    class Meta:
        model = Tag
        fields = ["name", "slug"]
