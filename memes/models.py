import textwrap

import PIL
from PIL import Image, ImageDraw, ImageFont
from django import forms
from django.db import models


class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()


class ImageSrc(models.Model):
    path = models.CharField(max_length=200)

    def __str__(self):
        return self.path

    @staticmethod
    def handle_uploaded_file(f, destination_path):
        with open(destination_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)


class Mem(models.Model):
    image = models.ForeignKey(ImageSrc, on_delete=models.CASCADE)
    path = models.CharField(max_length=200)
    upper_text = models.CharField(max_length=200)
    lower_text = models.CharField(max_length=200)

    @staticmethod
    def generate_meme(image_path,
                      dst_path,
                      top_text,
                      bottom_text='',
                      font_path='',
                      font_size=9,
                      stroke_width=5):
        # load image
        im = PIL.Image.open(image_path)

        draw = ImageDraw.Draw(im)
        image_width, image_height = im.size

        # load font
        font = ImageFont.truetype(font=font_path, size=int(image_height * font_size) // 100)

        # convert text to uppercase
        top_text = top_text.upper()
        bottom_text = bottom_text.upper()

        # text wrapping
        char_width, char_height = font.getsize('A')
        chars_per_line = image_width // char_width
        top_lines = textwrap.wrap(top_text, width=chars_per_line)
        bottom_lines = textwrap.wrap(bottom_text, width=chars_per_line)

        # draw top lines
        y = 10
        for line in top_lines:
            line_width, line_height = font.getsize(line)
            x = (image_width - line_width) / 2
            draw.text((x, y), line, fill='white', font=font, stroke_width=stroke_width, stroke_fill='black')
            y += line_height

        # draw bottom lines
        y = image_height - char_height * len(bottom_lines) - 15
        for line in bottom_lines:
            line_width, line_height = font.getsize(line)
            x = (image_width - line_width) / 2
            draw.text((x, y), line, fill='white', font=font, stroke_width=stroke_width, stroke_fill='black')
            y += line_height

        # save meme
        im.save(dst_path)

    def __str__(self):
        return self.image
