"""Back-office catalog management: access control, CRUD round-trips, validation."""

from decimal import Decimal
from http import HTTPStatus

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from .forms import MAX_IMAGE_BYTES, ProductForm
from .models import Category, Product, Tag

pytestmark = pytest.mark.django_db


def manage_urls(product, tag):
    """Every staff-only catalog URL, for the access-control sweeps."""
    return [
        reverse("products:manage_products"),
        reverse("products:manage_product_create"),
        reverse("products:manage_product_update", kwargs={"pk": product.pk}),
        reverse("products:manage_product_delete", kwargs={"pk": product.pk}),
        reverse("products:manage_catalog"),
        reverse("products:manage_category_create"),
        reverse("products:manage_category_update", kwargs={"pk": product.category.pk}),
        reverse("products:manage_tag_create"),
        reverse("products:manage_tag_update", kwargs={"pk": tag.pk}),
    ]


def product_data(category, **overrides):
    data = {
        "name": "MindSync Sleep Halo",
        "slug": "mindsync-sleep-halo",
        "tagline": "Dream in someone else's 4K.",
        "description": "A bedside accessory for the MindSync line.",
        "price": "199.99",
        "is_available": "on",
        "category": str(category.pk),
    }
    data.update(overrides)
    return data


# --- Access control ----------------------------------------------------------


def test_anonymous_users_are_sent_to_login(client, product, tag):
    for url in manage_urls(product, tag):
        response = client.get(url)

        assert response.status_code == HTTPStatus.FOUND, url
        assert reverse("accounts:login") in response.url


def test_customers_get_403(client, customer, product, tag):
    client.force_login(customer)

    for url in manage_urls(product, tag):
        assert client.get(url).status_code == HTTPStatus.FORBIDDEN, url


def test_staff_get_200(client, staff_user, product, tag):
    client.force_login(staff_user)

    for url in manage_urls(product, tag):
        response = client.get(url)

        assert response.status_code == HTTPStatus.OK, url
        # A multi-line {# #} comment renders as literal text — guard
        # against template comments leaking onto the page.
        assert "{#" not in response.content.decode(), url


def test_navbar_shows_back_office_to_staff_only(client, staff_user, customer):
    client.force_login(staff_user)
    assert "Back office" in client.get(reverse("products:catalog")).content.decode()

    client.force_login(customer)
    assert "Back office" not in client.get(reverse("products:catalog")).content.decode()


# --- Product CRUD ------------------------------------------------------------


def test_staff_can_create_a_product(client, staff_user, category, tag):
    client.force_login(staff_user)

    response = client.post(
        reverse("products:manage_product_create"),
        product_data(category, tags=[str(tag.pk)]),
        follow=True,
    )

    product = Product.objects.get(slug="mindsync-sleep-halo")
    assert product.price == Decimal("199.99")
    assert product.category == category
    assert list(product.tags.all()) == [tag]
    assert "created." in response.content.decode()


def test_staff_can_edit_a_price(client, staff_user, product):
    client.force_login(staff_user)
    data = product_data(product.category, name=product.name, slug=product.slug)
    data["price"] = "299.99"

    client.post(
        reverse("products:manage_product_update", kwargs={"pk": product.pk}), data
    )

    product.refresh_from_db()
    assert product.price == Decimal("299.99")


def test_staff_can_mark_a_product_unavailable(client, staff_user, product):
    client.force_login(staff_user)
    data = product_data(product.category, name=product.name, slug=product.slug)
    del data["is_available"]  # an unchecked checkbox is simply absent

    client.post(
        reverse("products:manage_product_update", kwargs={"pk": product.pk}), data
    )

    product.refresh_from_db()
    assert not product.is_available


def test_staff_can_delete_a_product(client, staff_user, product):
    client.force_login(staff_user)

    response = client.post(
        reverse("products:manage_product_delete", kwargs={"pk": product.pk})
    )

    assert response.url == reverse("products:manage_products")
    assert not Product.objects.exists()


def test_manage_list_shows_unavailable_products(
    client, staff_user, unavailable_product
):
    client.force_login(staff_user)

    page = client.get(reverse("products:manage_products")).content.decode()

    assert unavailable_product.name in page
    assert "Unavailable" in page


def test_manage_list_shows_a_thumbnail_for_every_product(
    client, staff_user, product, unavailable_product, photo
):
    product.image.save("photo.png", photo)
    client.force_login(staff_user)

    page = client.get(reverse("products:manage_products")).content.decode()

    assert f'src="{product.image.url}"' in page
    assert 'src="/static/images/placeholders/home-assistants.svg"' in page


# --- Product photos ----------------------------------------------------------


def test_form_accepts_a_photo(category, photo):
    form = ProductForm(product_data(category), {"image": photo})

    assert form.is_valid(), form.errors
    assert form.save().image.name.startswith("products/photo")


def test_form_rejects_a_file_that_is_not_an_image(category):
    notes = SimpleUploadedFile("notes.txt", b"not an image", content_type="text/plain")

    form = ProductForm(product_data(category), {"image": notes})

    assert not form.is_valid()
    assert "Upload a valid image" in form.errors["image"][0]


def test_form_rejects_a_photo_over_the_size_limit(category, photo):
    # A real image padded past the limit: still an image, just too big.
    oversized = SimpleUploadedFile(
        "huge.png", photo.read() + b"\0" * MAX_IMAGE_BYTES, content_type="image/png"
    )

    form = ProductForm(product_data(category), {"image": oversized})

    assert not form.is_valid()
    assert "at most 2 MB" in form.errors["image"][0]


def test_form_clears_a_photo(product, photo):
    product.image.save("photo.png", photo)
    data = product_data(product.category, name=product.name, slug=product.slug)
    data["image-clear"] = "on"

    form = ProductForm(data, instance=product)

    assert form.is_valid(), form.errors
    assert not form.save().image


def test_staff_can_create_a_product_with_a_photo(
    client, staff_user, category, photo, media_root
):
    client.force_login(staff_user)

    client.post(
        reverse("products:manage_product_create"),
        product_data(category, image=photo),
    )

    product = Product.objects.get(slug="mindsync-sleep-halo")
    assert (media_root / product.image.name).is_file()


def test_staff_can_add_a_photo_to_a_product(
    client, staff_user, product, photo, media_root
):
    client.force_login(staff_user)
    data = product_data(product.category, name=product.name, slug=product.slug)

    client.post(
        reverse("products:manage_product_update", kwargs={"pk": product.pk}),
        data | {"image": photo},
    )

    product.refresh_from_db()
    assert (media_root / product.image.name).is_file()


def test_edit_form_shows_the_current_image(client, staff_user, product, photo):
    client.force_login(staff_user)
    url = reverse("products:manage_product_update", kwargs={"pk": product.pk})

    assert 'src="/static/images/placeholders/home-assistants.svg"' in (
        client.get(url).content.decode()
    )

    product.image.save("photo.png", photo)
    page = client.get(url).content.decode()

    assert f'src="{product.image.url}"' in page
    assert 'enctype="multipart/form-data"' in page


# --- Form validation ---------------------------------------------------------


def test_price_must_be_positive(client, staff_user, category):
    client.force_login(staff_user)

    response = client.post(
        reverse("products:manage_product_create"),
        product_data(category, price="-12.00"),
    )

    assert response.status_code == HTTPStatus.OK
    assert "greater than or equal to 0.01" in response.content.decode()
    assert not Product.objects.exists()


def test_slug_must_be_unique(client, staff_user, product):
    client.force_login(staff_user)

    response = client.post(
        reverse("products:manage_product_create"),
        product_data(product.category, slug=product.slug),
    )

    assert response.status_code == HTTPStatus.OK
    assert "already exists" in response.content.decode()
    assert Product.objects.count() == 1


def test_name_is_required(client, staff_user, category):
    client.force_login(staff_user)

    response = client.post(
        reverse("products:manage_product_create"), product_data(category, name="")
    )

    assert response.status_code == HTTPStatus.OK
    assert "This field is required." in response.content.decode()
    assert not Product.objects.exists()


# --- Categories and tags -----------------------------------------------------


def test_staff_can_create_and_edit_a_category(client, staff_user):
    client.force_login(staff_user)

    client.post(
        reverse("products:manage_category_create"),
        {"name": "Defense", "slug": "defense"},
    )
    category = Category.objects.get(slug="defense")

    client.post(
        reverse("products:manage_category_update", kwargs={"pk": category.pk}),
        {"name": "Home Defense", "slug": "defense"},
    )

    category.refresh_from_db()
    assert category.name == "Home Defense"


def test_staff_can_create_and_edit_a_tag(client, staff_user):
    client.force_login(staff_user)

    client.post(
        reverse("products:manage_tag_create"),
        {"name": "new arrival", "slug": "new-arrival"},
    )
    tag = Tag.objects.get(slug="new-arrival")

    client.post(
        reverse("products:manage_tag_update", kwargs={"pk": tag.pk}),
        {"name": "just landed", "slug": "new-arrival"},
    )

    tag.refresh_from_db()
    assert tag.name == "just landed"


def test_manage_catalog_lists_categories_and_tags(client, staff_user, product, tag):
    client.force_login(staff_user)

    page = client.get(reverse("products:manage_catalog")).content.decode()

    assert product.category.name in page
    assert tag.name in page
