from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from openid.store.filestore import FileOpenIDStore
from openid.consumer.consumer import Consumer
from openid.extensions import ax, pape, sreg


PAPE_POLICIES = (
    'AUTH_PHISHING_RESISTANT',
    'AUTH_MULTI_FACTOR',
    'AUTH_MULTI_FACTOR_PHYSICAL',
)


def begin(request):
    if request.method == "GET":
        return render(request, "userauth/openid.html")

    auth_url = request.POST['url']
    store = FileOpenIDStore("/tmp/overmind_openid_store")
    consumer = Consumer(request.session, store)
    try:
        auth_req = consumer.begin(auth_url)
    except Exception as err:
        return HttpResponse("{}: {}".format(type(err).__name__, err))

    sreg_req = sreg.SRegRequest(optional=["email", "nickname"],
                                    required=["dob"])
    auth_req.addExtension(sreg_req)

    ax_req = ax.FetchRequest()
    ax_req.add(ax.AttrInfo('http://schema.openid.net/namePerson',
                           required=True))
    ax_req.add(ax.AttrInfo('http://schema.openid.net/contact/web/default',
                            required=False, count=ax.UNLIMITED_VALUES))
    auth_req.addExtension(ax_req)

    pape_req = pape.Request([getattr(pape, p) for p in PAPE_POLICIES])
    auth_req.addExtension(pape_req)


    if auth_req.shouldSendRedirect():
        url = auth_req.redirectURL(reverse("userauth:openid-begin"),
                                   reverse("userauth:openid-complete"))
        return redirect(url)

    form_html = auth_req.formMarkup(
            reverse("userauth:openid-begin"),
            reverse("userauth:openid-complete"),
            False, {'id': "openid_message"})
    return render(request, "userauth/openid_form.html", {"form_html": form_html})


def complete(request):
    import pdb; pdb.set_trace()
