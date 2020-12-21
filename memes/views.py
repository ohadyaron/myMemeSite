import mimetypes
import os

from django.conf import settings
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic

from .models import Mem, ImageSrc


def upload(request):
    if request.method == 'POST':
        f = request.FILES['file']
        obj = ImageSrc.objects.latest('id')
        filename = str(obj.id + 1) + '.jpeg'
        arr = os.listdir(settings.STATICFILES_DIRS[0] + settings.IMAGES_DIR)
        if filename in arr:
            print('exists ' + filename)
            filename = '_' + filename

        destination_path = settings.STATICFILES_DIRS[0] + settings.IMAGES_DIR + filename
        ImageSrc.handle_uploaded_file(f, destination_path=destination_path)
        ImageSrc.objects.get_or_create(path=settings.IMAGES_DIR + filename)
        image = ImageSrc.objects.filter(path=settings.IMAGES_DIR + filename)[0]
        return HttpResponseRedirect(reverse('memes:image', args=(image.id,)))


def load_images():
    for file in os.listdir(settings.STATICFILES_DIRS[0] + settings.IMAGES_DIR):
        try:
            ImageSrc.objects.get_or_create(path=settings.IMAGES_DIR + file)
            print("inserted " + file)
        except (KeyError, ImageSrc.DoesNotExist):
            print("already exists " + file)


class IndexView(generic.ListView):
    template_name = 'memes/index.html'
    context_object_name = 'latest_images_list'

    load_images()

    def get_queryset(self):
        """Return 20 static images."""
        return ImageSrc.objects.all()


class ImageSrcView(generic.DetailView):
    model = ImageSrc
    context_object_name = 'image'
    template_name = 'memes/image.html'


class MemView(generic.DetailView):
    model = Mem
    template_name = 'memes/mem.html'


def set_text(request, image_id):
    selected_image = get_object_or_404(ImageSrc, pk=image_id)
    try:
        print("new mem " + selected_image.path)
        upper_text = request.POST.get('utext')
        lower_text = request.POST.get('ltext')
        mem = Mem.objects.get_or_create(image=selected_image,
                                        upper_text=upper_text,
                                        lower_text=lower_text)[0]
        mem.path = settings.MEMES_DIR + str(mem.id) + '.jpeg'
        mem.save()
        Mem.generate_meme(image_path=settings.STATICFILES_DIRS[0] + selected_image.path,
                          font_path=settings.STATICFILES_DIRS[0] + '/fonts/impact/impact.ttf',
                          dst_path=settings.STATICFILES_DIRS[0] + mem.path,
                          top_text=upper_text,
                          bottom_text=lower_text)
        return HttpResponseRedirect(reverse('memes:meme', args=(mem.id,)))
    except (KeyError, Mem.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'memes/image.html', {
            'mem': image_id,
            'error_message': "You didn't select a text.",
        })


def download(request, mem_id):
    file_path = settings.STATICFILES_DIRS[0] + settings.MEMES_DIR + str(mem_id) + '.jpeg'
    print('download ' + file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            mime_type, _ = mimetypes.guess_type(file_path)
            response = HttpResponse(fh.read(), content_type=mime_type)
            response['Content-Disposition'] = 'attachment; filename=' + os.path.basename(file_path)
            return response
    raise Http404
