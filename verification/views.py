"""The public verification page.

This is the one page a stranger opens, from a QR code, with no account and no
way to ask for help if it fails. So it does the least work of any page in the
system: one indexed lookup, one row written, one verdict rendered. It requires
no session, loads no script, and depends on no component other than products.

The three verdicts are the whole contract. An unmatched code returns Not found
rather than a guess, because a wrong verdict does real harm in both directions:
calling a counterfeit genuine misleads a buyer, and calling a genuine product
counterfeit damages a producer who did nothing wrong.

Sprint 3 adds the chain of custody to the page (FR32), the scan-event region
(FR33), the duplicate-scan alert (FR49) and the per-IP cap (FR58); each of
those is one extra query and none of them sits on the answer's path.
"""

from datetime import timedelta

from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils import timezone

from products.models import Alert, AlertKind, Product, ProductStatus, TransferState

from .models import DeviceCategory, ScanEvent, Verdict

#: One passport scanned from two different regions inside a window is the
#: signal that one of the two scans is a cloned QR. The window is the 24 hours
#: the logistics team considered the fastest a genuine product could cross the
#: country; longer would miss same-city cloning, shorter would flag a
#: legitimate courier handover.
DUPLICATE_SCAN_WINDOW = timedelta(hours=24)

#: FR58 caps scan events at sixty per source address per hour. Past the cap
#: the verdict is still answered; only the record is dropped, because a buyer
#: holding a real product must never be refused an answer.
SCAN_CAP_PER_HOUR = 60


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


def _client_ip(request):
    return request.META.get("REMOTE_ADDR") or "0.0.0.0"


def _region_for(request):
    """The coarse geographic region of the scan.

    For now we answer with the country/region header a CDN sets, falling back
    to "CO" because the project ships for Colombian producers first. Real
    deployments add a MaxMind lookup; the field is wide enough for any of
    them.
    """
    return request.META.get("HTTP_CF_IPCOUNTRY") or request.META.get("HTTP_X_APPENGINE_COUNTRY") or "CO"


def _under_scan_cap(ip):
    key = f"scan-cap:{ip}"
    count = cache.get(key)
    if count is None:
        cache.set(key, 1, timeout=3600)
        return True
    if count >= SCAN_CAP_PER_HOUR:
        return False
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=3600)
    return True


def verify(request, code):
    """FR28 without a session, FR29 Genuine, FR30 Revoked, FR31 Not found."""
    product = Product.objects.select_related("company").filter(passport_code=code).first()

    if product is None:
        verdict = Verdict.NOT_FOUND
    elif product.status == ProductStatus.REVOKED:
        verdict = Verdict.REVOKED
    else:
        verdict = Verdict.GENUINE

    ip = _client_ip(request)
    if _under_scan_cap(ip):
        region = _region_for(request)
        scan = ScanEvent.objects.create(
            product=product,
            verdict=verdict,
            region=region,
            device_category=_device_category(request.META.get("HTTP_USER_AGENT")),
        )

        # FR49: one passport scanned in two different regions within a window
        # is the signal that one of the two scans is a cloned QR.
        if product is not None and region:
            is_duplicate = (
                ScanEvent.objects.filter(
                    product=product,
                    scanned_at__gte=timezone.now() - DUPLICATE_SCAN_WINDOW,
                )
                .exclude(region=region)
                .exclude(pk=scan.pk)
                .exists()
            )
            if is_duplicate:
                Alert.objects.get_or_create(
                    product=product, scan=scan, defaults={"kind": AlertKind.DUPLICATE_SCAN}
                )
    else:
        scan = None

    # FR32: the chain of custody, oldest first, with only the receiver's
    # public name. A revoked product still shows its chain: a buyer needs to
    # see where the chain stopped.
    chain = []
    if product is not None:
        chain = (
            product.custody_transfers.filter(state=TransferState.ACCEPTED)
            .select_related("from_holder", "to_holder")
            .order_by("created_at")
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
            "chain": chain,
        },
    )


def lookup(request):
    """Typing a code by hand, for a QR that will not scan or a code read aloud."""
    code = request.GET.get("code", "").strip()
    if code:
        return redirect("verification:verify", code=code)
    return render(request, "verification/lookup.html")
