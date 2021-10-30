# -*- coding: utf-8 -*-
#  This Lektor plugin is using ImageMagic (convert)
#  to convert images to different pre-configured thumbnails
#  as .jpg and .webp.

import shutil

from lektor.build_programs import AttachmentBuildProgram, buildprogram
from lektor.context import get_ctx
from lektor.db import Image
from lektor.imagetools import (compute_dimensions, find_imagemagick,
                               get_image_info, get_quality)
from lektor.pluginsystem import Plugin
from lektor.reporter import reporter
from lektor.utils import portable_popen
from werkzeug.utils import cached_property


# We override process_image here because Lektor does not support adding extra
# parameters yet, but maybe it will soon, and this can be removed when it does.
def process_image(
    ctx,
    source_image,
    dst_imagename,
    width=None,
    height=None,
    quality=None,
    extra_params=None,
    resize_image=True,
    file_format=None,
):
    """Build image from source image, optionally compressing and resizing.
    "source_image" is the absolute path of the source in the content directory,
    "dst_imagename" is the absolute path of the target in the output directory.
    """
    reporter.report_debug_info("processing image:", dst_imagename)
    if width is None and height is None:
        raise ValueError("Must specify at least one of width or height.")

    convert = find_imagemagick(ctx.build_state.config["IMAGEMAGICK_EXECUTABLE"])
    cmdline = [convert, source_image, "-auto-orient"]

    if quality is None:
        quality = get_quality(source_image)

    if resize_image:
        resize_key = ""
        if width is not None:
            resize_key += str(width)
        if height is not None:
            resize_key += "x" + str(height)
        cmdline += ["-resize", resize_key]

    if file_format == 'webp':
        cmdline += ['-define', 'webp:lossless=false']

    if extra_params:
        cmdline.extend(extra_params)

    cmdline += ['-define', 'thread-level=1']
    cmdline += ["-quality", str(quality), dst_imagename]

    reporter.report_debug_info("imagemagick cmd line", cmdline)
    portable_popen(cmdline).wait()


@buildprogram(Image)
class ResizedImageBuildProgram(AttachmentBuildProgram):
    """
      Build all images in lektor content at initialisation...
    """
    def build_artifact(self, artifact):
        ctx = get_ctx()
        plugin = ctx.env.plugins["image-resize"]
        config = plugin.config

        artifact.ensure_dir()
        AttachmentBuildProgram.build_artifact(self, artifact)

        if not config:
            return

        source_img = artifact.source_obj.attachment_filename

        with open(source_img, "rb") as file:
            _, _width, _height = get_image_info(file)

        # For every section in the config, we need to generate one image.
        for item, conf in config.items():
            width = int(conf.get("width", 0))
            height = int(conf.get("height", "0"))
            filename = artifact.source_obj.url_path
            ext_pos = filename.rfind(".")
            filename_prefix = "%s-%s" % (filename[:ext_pos], item)
            filename_suffixes = ['jpg', 'webp']
            """
              makeing sure width and height are defined
            """
            if width < 1:
                if height < 1:
                    width = int(1280)
                    height = int(720)
                    print(f"WARNING: No size detected for {filename_prefix}, falling back to 1280x720. Plese define at least width or height in 'configs/image-resize.ini'!")
                else:
                    _, width = compute_dimensions(height, None, _height, _width)
            if height < 1:
                _, height = compute_dimensions(width, None, _width, _height)

            for filename_suffix in filename_suffixes:
                """
                    run loop for each file we want to export
                """
                def closure(filename_prefix, filename_suffix, source_img, width, height, resize_image=True, ):
                # We need this closure, otherwise variables get updated and this
                # doesn't work at all.
                    dst_filename = f"{filename_prefix}.{filename_suffix}"
                    @ctx.sub_artifact(artifact_name=dst_filename, sources=[source_img])
                    def build_thumbnail_artifact(artifact):
                        artifact.ensure_dir()
                        if not resize_image and filename_suffix != 'webp':
                            shutil.copy2(source_img, artifact.dst_filename)
                        else:
                            process_image(
                                ctx,
                                source_img,
                                artifact.dst_filename,
                                width,
                                height,
                                quality=89,
                                extra_params=['-strip', '-interlace', 'Plane',],
                                resize_image=resize_image,
                                file_format=filename_prefix,
                            )
                resize_image = _width > width or _height > height
                closure(filename_prefix, filename_suffix, source_img, width, height, bool(resize_image))


class ImageResizePlugin(Plugin):
    name = "thumbnail-generator"
    description = "Generate JPG and WEBP Images and Thumbnails in predefined sizes."
    image_exts = ["jpg", "webp"]

    @cached_property
    def config(self):
        conf = self.get_config()
        return {section: conf.section_as_dict(section) for section in conf.sections()}
