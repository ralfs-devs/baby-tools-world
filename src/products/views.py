from django.contrib import messages
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm
from .models import Category, Comment, Product


def product_list(request, category_slug=None):
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


def product_detail(request, category_slug, pk):
    """Display a product detail page with comments and review form.

    Handles POST submissions to create/update comments and implements
    form clearing after successful submission via session flag.

    Args:
        request: The HTTP request object.
        category_slug: Category slug for URL resolution.
        pk: Primary key of the product.

    Returns:
        HttpResponse with rendered product.html template.
    """
    product = get_object_or_404(
        Product.objects.select_related("category").annotate(
            avg_rating=Avg("comments__rating"), total_ratings=Count("comments")
        ),
        pk=pk,
        category__slug=category_slug,
    )
    related_products = (
        Product.objects.filter(category=product.category)
        .exclude(pk=product.pk)
        .annotate(avg_rating=Avg("comments__rating"), total_ratings=Count("comments"))
        .order_by("-avg_rating", "-total_ratings", "name")[:8]
    )
    comments = product.comments.select_related("user").order_by("-created_at")

    if request.method == "POST":
        form = CommentForm(request.POST, initial={"user": request.user if request.user.is_authenticated else None})
        if form.is_valid():
            rating = form.cleaned_data["rating"]
            text = form.cleaned_data.get("text", "")

            if request.user.is_authenticated:
                comment, created = Comment.objects.get_or_create(
                    product=product, user=request.user, defaults={"rating": rating, "text": text}
                )
                if not created:
                    comment.rating = rating
                    comment.text = text
                    comment.save()
                messages.success(request, "Your rating was {}.".format("submitted" if created else "updated"))
            else:
                comment = form.save(commit=False)
                comment.product = product
                comment.save()
                messages.success(request, "Thank you for your rating.")

            request.session["form_reset_product_pk"] = product.pk
            return redirect("product_detail", category_slug=category_slug, pk=product.pk)
    else:
        initial = {}
        if request.user.is_authenticated:
            existing = product.comments.filter(user=request.user).first()
            if existing and request.session.pop("form_reset_product_pk", None) != product.pk:
                initial = {"rating": existing.rating, "text": existing.text}
        form = CommentForm(initial=initial)

    return render(
        request,
        "product.html",
        {"product": product, "comments": comments, "related_products": related_products, "form": form},
    )