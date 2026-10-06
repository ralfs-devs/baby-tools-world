from django.contrib import messages
from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm
from .models import Category, Comment, Product


def product_list(request: HttpRequest, category_slug: str | None = None) -> HttpResponse:
    """Return a list of products with their rating aggregates.

    Args:
        request: The HTTP request object.
        category_slug: Optional slug to filter by category.

    Returns:
        HttpResponse with rendered products.html template.
    """
    categories = Category.objects.all()
    products = Product.objects.select_related("category").annotate(
        avg_rating=Avg("comments__rating"), total_ratings=Count("comments")
    )
    if category_slug:
        products = products.filter(category__slug=category_slug)
    return render(request, "products.html", {"categories": categories, "products": products})


def _get_detailed_product(category_slug: str, pk: int) -> Product:
    """Fetch a product with category and rating aggregates.

    Args:
        category_slug: Category slug for lookup.
        pk: Primary key of the product.

    Returns:
        Product annotated with average rating and total rating count.

    Raises:
        Http404: If no matching product exists.
    """
    return get_object_or_404(
        Product.objects.select_related("category").annotate(
            avg_rating=Avg("comments__rating"), total_ratings=Count("comments")
        ),
        pk=pk,
        category__slug=category_slug,
    )


def _get_related_products(product: Product) -> list[Product]:
    """Return up to eight related products of the same category.

    Args:
        product: Reference product defining the category.

    Returns:
        List of products ordered by rating, rating count, and name.
    """
    query = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .annotate(avg_rating=Avg("comments__rating"), total_ratings=Count("comments"))
        .order_by("-avg_rating", "-total_ratings", "name")[:8]
    )
    return list(query)


def _save_authenticated_rating(request: HttpRequest, product: Product, form: CommentForm) -> None:
    """Create or update the authenticated user's comment.

    Args:
        request: The HTTP request object.
        product: Product the rating belongs to.
        form: Validated comment form instance.
    """
    rating = form.cleaned_data["rating"]
    text = form.cleaned_data.get("text", "")
    comment, created = Comment.objects.get_or_create(
        product=product, user=request.user, defaults={"rating": rating, "text": text}
    )
    if not created:
        comment.rating = rating
        comment.text = text
        comment.save()
    messages.success(request, "Your rating was {}.".format("submitted" if created else "updated"))


def _save_anonymous_rating(request: HttpRequest, form: CommentForm, product: Product) -> None:
    """Save an anonymous rating from a validated form.

    Args:
        request: The HTTP request object.
        form: Validated comment form instance.
        product: Product the rating belongs to.
    """
    comment = form.save(commit=False)
    comment.product = product
    comment.save()
    messages.success(request, "Thank you for your rating.")


def _submit_rating(
    request: HttpRequest, product: Product, category_slug: str
) -> tuple[CommentForm, HttpResponse | None]:
    """Validate and persist a submitted rating.

    Args:
        request: The HTTP request object.
        product: Product being rated.
        category_slug: Category slug for URL resolution.

    Returns:
        The bound form together with a redirect on success,
        or the form and None if validation failed.
    """
    form = CommentForm(request.POST, initial={"user": request.user if request.user.is_authenticated else None})
    if not form.is_valid():
        return form, None
    if request.user.is_authenticated:
        _save_authenticated_rating(request, product, form)
    else:
        _save_anonymous_rating(request, form, product)
    request.session["form_reset_product_pk"] = product.pk
    return form, redirect("product_detail", category_slug=category_slug, pk=product.pk)


def _build_form(request: HttpRequest, product: Product) -> CommentForm:
    """Build an empty form, restoring previous values if applicable.

    Args:
        request: The HTTP request object.
        product: Product whose comments are checked for the current user.

    Returns:
        CommentForm with initial data from the user's existing comment.
    """
    initial = {}
    if request.user.is_authenticated:
        existing = product.comments.filter(user=request.user).first()
        if existing and request.session.pop("form_reset_product_pk", None) != product.pk:
            initial = {"rating": existing.rating, "text": existing.text}
    return CommentForm(initial=initial)


def product_detail(request: HttpRequest, category_slug: str, pk: int) -> HttpResponse:
    """Display a product detail page with comments and review form.

    Args:
        request: The HTTP request object.
        category_slug: Category slug for URL resolution.
        pk: Primary key of the product.

    Returns:
        Redirect after a successful rating submission, otherwise
        the rendered product.html template.
    """
    product = _get_detailed_product(category_slug, pk)
    related_products = _get_related_products(product)
    comments = product.comments.select_related("user").order_by("-created_at")
    if request.method == "POST":
        form, response = _submit_rating(request, product, category_slug)
        if response is not None:
            return response
    else:
        form = _build_form(request, product)
    return render(
        request,
        "product.html",
        {"product": product, "comments": comments, "related_products": related_products, "form": form},
    )
