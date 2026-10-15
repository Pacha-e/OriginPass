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

import re
import unicodedata
from datetime import timedelta

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.utils import timezone

from companies.models import Company, CompanyStatus
from products.models import Alert, AlertKind, Product, ProductStatus, TransferState

from .models import DeviceCategory, ScanEvent, Verdict

#: One passport scanned from two different regions inside a window is the
#: signal that one of the two scans is a cloned QR. A day is long enough to
#: catch a copy being scanned in another city the same day, and short enough
#: that a product moving between regions over a week does not alert. It is a
#: starting value to tune against real scans, not a measured one.
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


#: What a region may contain once read from a header: letters (accented too),
#: digits, spaces, dots and hyphens. Anything else is dropped, not escaped.
_REGION_NOISE = re.compile(r"[^\w .-]")
_REGION_LENGTH = ScanEvent._meta.get_field("region").max_length


def _region_for(request):
    """The coarse geographic region of the scan, or blank when it is not known.

    Read from the headers a CDN adds: the first-level region when it sends one
    (Cloudflare's visitor location headers), otherwise the country. Outside such
    a proxy the client writes those headers itself, so they are only read when
    the deployment says they can be trusted (TRUST_GEO_HEADERS). A value from a
    header is input like any other: it is cleaned and cut to the column, so a
    long or odd header cannot take the page down.
    """
    if not settings.TRUST_GEO_HEADERS:
        return ""
    raw = (
        request.META.get("HTTP_CF_REGION")
        or request.META.get("HTTP_CF_IPCOUNTRY")
        or request.META.get("HTTP_X_APPENGINE_COUNTRY")
        or ""
    )
    return _REGION_NOISE.sub("", raw).strip()[:_REGION_LENGTH]


def _under_scan_cap(ip):
    """Count this scan against the hourly cap of its address (FR58).

    `add` and `incr` are each atomic in the cache, so two scans arriving
    together cannot both read the same count and both slip under the cap.
    """
    key = f"scan-cap:{ip}"
    if cache.add(key, 1, timeout=3600):
        return True
    try:
        count = cache.incr(key)
    except ValueError:
        # The key expired between the two calls; this scan opens a new hour.
        cache.set(key, 1, timeout=3600)
        return True
    return count <= SCAN_CAP_PER_HOUR


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
                .exclude(region="")
                .exclude(pk=scan.pk)
                .exists()
            )
            if is_duplicate:
                Alert.objects.get_or_create(
                    product=product, scan=scan, defaults={"kind": AlertKind.DUPLICATE_SCAN}
                )
    else:
        scan = None

    # FR32: the chain of custody, oldest first. A revoked product still shows
    # its chain: a buyer needs to see where the chain stopped.
    chain = _public_chain(product) if product is not None else []

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
            "mrz": _machine_readable_zone(product) if product is not None else "",
        },
    )


#: Width of a line of the machine-readable zone of a passport (ICAO 9303, TD3).
_MRZ_WIDTH = 44


def _machine_readable_zone(product):
    """The two-line strip printed at the foot of a passport data page.

    Decoration in the vernacular of the document the page imitates, hidden from
    assistive technology: the same facts are on the page in words. Built from
    what the page already shows, so it reveals nothing new.
    """
    plain = unicodedata.normalize("NFKD", product.name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^A-Z0-9]+", "<", plain.upper()).strip("<")
    first = f"OP<COL<{name}".ljust(_MRZ_WIDTH, "<")[:_MRZ_WIDTH]
    second = f"{product.passport_code}<{product.registered_at:%y%m%d}".ljust(_MRZ_WIDTH, "<")
    return f"{first}\n{second[:_MRZ_WIDTH]}"


def _public_chain(product):
    """Each accepted handover, named the way a stranger may see it.

    The page is public, so an account is never shown by its email address. A
    holder that is an approved company is shown by its registered name, which
    is already public on its profile; anyone else is a private holder.
    """
    transfers = list(
        product.custody_transfers.filter(state=TransferState.ACCEPTED)
        .select_related("to_holder")
        .order_by("created_at")
    )
    companies = {
        company.owner_id: company
        for company in Company.objects.filter(
            owner__in=[transfer.to_holder for transfer in transfers],
            status=CompanyStatus.APPROVED,
        )
    }
    return [
        {
            "company": companies.get(transfer.to_holder_id),
            "note": transfer.note,
            "date": transfer.resolved_at,
        }
        for transfer in transfers
    ]


def lookup(request):
    """Typing a code by hand, for a QR that will not scan or a code read aloud."""
    code = request.GET.get("code", "").strip()
    if code:
        return redirect("verification:verify", code=code)
    return render(request, "verification/lookup.html")
