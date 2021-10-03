 lektor image resize plugin
============================

[![PyPI version](https://badge.fury.io/py/lektor-image-resize.svg)](https://badge.fury.io/py/lektor-image-resize)
[![Downloads](https://pepy.tech/badge/lektor-image-resize)](https://pepy.tech/project/lektor-image-resize)
[![Linting Python package](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpackage.yml)
[![Upload Python Package](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpublish.yml/badge.svg)](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpublish.yml)
[![MIT License](https://raw.githubusercontent.com/chaos-bodensee/lektor-image-resize/main/.github/license.svg?sanitize=true)](https://github.com/chaos-bodensee/lektor-image-resize/blob/main/LICENSE)


This plugin generates JPG and WEBP Images and Thumbnails in predefined sizes for any images in your [Lektor](https://getlektor.com) content.
The difference between this plugin and the lektor [thumbnail](https://www.getlektor.com/docs/api/db/record/thumbnail/) filter is that this plugin is converting all images and you don't need to have any references to the images in your templates.

 TL;DR: What does this plugin do?
---------------------------------
+ It will generate ``JPEG`` images in the sizes you configured of all images in your Lektor content using ``imagemagic``.
+ It will generate ``WEBP`` images in the same sizes using ``imagemagic``.

 Usage
-------
Use this plugin if you want to be able to link to full-size images in your content, but still want thumbnails to be generated for the link itself.
For example, you may have an image called ``waffle.jpg``, and to link to it in the content (not the template), but also show a thumbnail.
All images will be converted to webp using [Pillow](https://pypi.org/project/Pillow/).

You can use the images like that:
```html
<!-- Simple example -->
<a href="waffle.jpg"><img src="waffle-small.jpg" /></a>

<!-- example with srcset -->
<a href="waffle-woowee.webp">
  <img src="waffle-small.webp"
    srcset="waffle-small.webp  512w,   // Viewport bis zu 512
            waffle-medium.webp 900w,   // Viewport größer als 512
            waffle-woowee.webp 1440w"  // Viewport größer als 900
  />
</a>
```

 Installation
--------------
To install the plugin, add ``lektor-image-resize`` to your plugins from the command line and create a config file:
```bash
# add the plugin to lektor
lektor plugins add lektor-image-resize
```

If you have trouble, see the [plugin
installation](https://www.getlektor.com/docs/plugins/) section of the Lektor
documentation.

Create a config file called `configs/image-resize.ini` and add
a few sections for images. The section names can be whatever you want, the
final images will be called ``$(imagename)-$(sectionname).jpg`` and ``$(imagename)-$(sectionname).webp``.

Here is a example config file:

```ini
[small]
max_width = 512

[medium]
max_width = 900
max_height = 900

[woowee]
max_width = 1440
```

Will take a file called `waffle.jpg` and create the files `waffle-small.jpg`,
`waffle-medium.jpg` and `waffle-woowee.jpg` as well as `waffle-small.webp`,
`waffle-medium.webp` and `waffle-woowee.webp` All the files will be created,
regardless of whether the original file is smaller, so you can link without worrying
whether a file will exist or not. If the original file is smaller than the width
you have specified, the file will only be copied, and will not be resized.

The `max_width`/`max_height` parameters work like for the [Lektor
thumbnail](https://www.getlektor.com/docs/api/db/record/thumbnail/) command.

 Good to know
---------------
There is a filter plugin avaliable at [lektor-image-filter](https://github.com/chaos-bodensee/lektor-image-filter.git) available, that can help you to use the image in all configured sizes,
