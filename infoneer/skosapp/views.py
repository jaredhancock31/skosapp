from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect, HttpResponseNotAllowed
from django.core.urlresolvers import reverse
from django.contrib.auth import views, tokens, decorators
from django.views.generic import DetailView
from .models import RdfUpload, UploadForm
from common.util.skos_tool import SkosTool


def index(request):
    return render(request, 'skosapp/home.html')


def contact(request):
    return render(request, 'skosapp/basic.html', {'data': ['Email', 'fameri@txstate.edu']})


def about(request):
    return render(request, 'skosapp/basic.html', {'data': ['todo', 'todo']})


def upload(request):
    """
    If POST, this view will validate and attempt to save the RDFUpload instance to the
    database. If GET, serve the Upload form
    :param request: request
    :return: if POST, send RDF to the tool for parsing and display results, otherwise, return
                a rendering of the UploadForm
    """
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.save()

            # save to session for ease of use between views
            request.session['rdf'] = instance.id
            return HttpResponseRedirect(reverse('skos'))
    else:
        form = UploadForm()
    return render(request, 'skosapp/upload.html', {'form': form})


def skos(request):
    pk = request.session.get('rdf', default=None)

    if pk:
        rdf = RdfUpload.objects.get(pk=pk)
        skos_tool = SkosTool(rdf_path=rdf.rdf_file.path)
        skos_tool.parse()
        skos_tool.sort()
        results = skos_tool.get_metrics()

        return render(request, 'skosapp/results.html', {'results': results})
    else:
        return render(request, 'index')


