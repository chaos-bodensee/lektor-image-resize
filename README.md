 lektor image resize plugin
============================
[![PyPI version](https://badge.fury.io/py/lektor-image-resize.svg)](https://badge.fury.io/py/lektor-image-resize)
 [![Downloads](https://pepy.tech/badge/lektor-image-resize)](https://pepy.tech/project/lektor-image-resize)
 [![Linting Python package](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpackage.yml/badge.svg)](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpackage.yml)
 [![Upload Python Package](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpublish.yml/badge.svg)](https://github.com/chaos-bodensee/lektor-image-resize/actions/workflows/pythonpublish.yml)

This plugin automatically generates thumbnails for any images in your [Lektor](https://getlektor.com) content.
The difference between this plugin and the lektor [thumbnail](https://www.getlektor.com/docs/api/db/record/thumbnail/) filter is that this plugin is converting all images and you don't need to have any references to the images in your templates.

 TL;DR: What does this plugin do?
---------------------------------
+ It will generate ``JPEG`` images in the sizes you configured of all images in your Lektor content.
+ It try to optimize the images with the [guetzli](https://github.com/google/guetzli) JPEG encoder. *(You have to install the guetzli binary by yourself)*

 Usage
-------
Use this plugin if you want to be able to link to full-size images in your content, but still want thumbnails to be generated for the link itself. For example, you may have an image called ``waffle.jpg``, and to link to it in the content (not the template), but also show a thumbnail.

You can do that like so:
```html
<a href="waffle.jpg"><img src="waffle-small.jpg" /></a>
```

 Installation
--------------
To install the plugin, just add ``lektor-image-resize`` to your plugins from the command line:
```bash
lektor plugins add lektor-image-resize
```

You **have to install** the [guetzli](https://github.com/google/guetzli) JPEG encoder.
```bash
# example
apt install guetzli
```

If you have trouble, see the [plugin
installation](https://www.getlektor.com/docs/plugins/) section of the Lektor
documentation.

Then, create a config file called `configs/image-resize.ini` and add
a few sections for images. The section names can be whatever you want, the
final images will be called `imagename-sectionname.jpg`. For example, this
config file:

```ini
[small]
max_width = 256

[medium]
max_width = 800
max_height = 800

[woowee]
max_width = 2000
```

Will take a file called `waffle.jpg` and create the files `waffle-small.jpg`,
`waffle-medium.jpg` and `waffle-woowee.jpg`. All the files will be created, regardless
of whether the original file is smaller, so you can link without worrying
whether a file will exist or not. If the original file is smaller than the width
you have specified, the file will only be copied, and will not be resized.
The `max_width`/`max_height` parameters work like for the [Lektor
thumbnail](https://www.getlektor.com/docs/api/db/record/thumbnail/) command.
