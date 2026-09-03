"""The public verification page.

This is the one page a stranger opens, from a QR code, with no account and no
way to ask for help if it fails. So it does the least work of any page in the
system: one indexed lookup, one row written, one verdict rendered. It requires
no session, loads no script, and depends on no component other than products.

The three verdicts are the whole contract. An unmatched code returns Not found
rather than a guess, because a wrong verdict does real harm in both directions:
calling a counterfeit genuine misleads a buyer, and calling a genuine product
counterfeit damages a producer who did nothing wrong.
"""

from django.shortcuts import redirect, render

from products.models import Product, ProductStatus

from .models import DeviceCategory, ScanEvent, Verdict


def _device_category(user_agent):
    """A coarse class for the analytics, derived from what the browser sends."""
    agent = (user_agent or "").lower()
    if not agent:
        return DeviceCategory.UNKNOWN
    if "ipad" in agent or "tablet" in agent:
        return DeviceCategory.TABLET
    if "mobi" in agent or "android" in agent or "iphone" in agent:
        return DeviceCategory.MOBILE
    return DeviceCategory.DESKTOP


def verify(request, code):
    """FR28 without a session, FR29 Genuine, FR30 Revoked, FR31 Not found."""
    product = Product.objects.select_related("company").filter(passport_code=code).first()

    if product is None:
        verdict = Verdict.NOT_FOUND
    elif product.status == ProductStatus.REVOKED:
        verdict = Verdict.REVOKED
    else:
        verdict = Verdict.GENUINE

    # Written for every visit, including the ones that matched nothing: a run of
    # unmatched codes is somebody probing the code space, which is exactly the
    # signal that would be lost by recording only the successes.
    ScanEvent.objects.create(
        product=product,
        verdict=verdict,
        device_category=_device_category(request.META.get("HTTP_USER_AGENT")),
    )

    # Answered with 200 rather than 404. The page is a valid answer to a valid
    # question, and a 404 would let a browser or a scanner replace it with an
    # error screen of its own, which is the one thing this page cannot afford.
    return render(
        request,
        "verification/verdict.html",
        {
            "product": product if verdict != Verdict.NOT_FOUND else None,
            "verdict": verdict,
            "submitted_code": code,
        },
    )


def lookup(request):
    """Typing a code by hand, for a QR that will not scan or a code read aloud."""
    code = request.GET.get("code", "").strip()
    if code:
        return redirect("verification:verify", code=code)
    return render(request, "verification/lookup.html")
