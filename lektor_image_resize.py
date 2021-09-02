# -*- coding: utf-8 -*-
import os
import shutil

from webptools import cwebp

from lektor.build_programs import AttachmentBuildProgram, buildprogram
from lektor.context import get_ctx
from lektor.db import Image
from lektor.imagetools import (compute_dimensions, find_imagemagick,
                               get_image_info, get_quality)
from lektor.pluginsystem import Plugin
from lektor.reporter import reporter
from lektor.utils import portable_popen, locate_executable
from werkzeug.utils import cached_property

# We override process_image here because Lektor does not support adding extra
# parameters yet, but maybe it will soon, and this can be removed when it does.
def process_image(
    ctx,
    source_image,
    dst_jpegname,
    width=None,
    height=None,
    mode=None,
    quality=None,
    extra_params=None,
):
    """Build image from source image, optionally compressing and resizing.
    "source_image" is the absolute path of the source in the content directory,
    "dst_jpegname" is the absolute path of the target in the output directory.
    """
    reporter.report_debug_info("processing image:", dst_jpegname)
    if width is None and height is None:
        raise ValueError("Must specify at least one of width or height.")

    im = find_imagemagick(ctx.build_state.config["IMAGEMAGICK_EXECUTABLE"])

    if quality is None:
        quality = get_quality(source_image)

    resize_key = ""
    if width is not None:
        resize_key += str(width)
    if height is not None:
        resize_key += "x" + str(height)

    cmdline = [im, source_image, "-auto-orient"]
    cmdline += ["-resize", resize_key]

    if extra_params:
        cmdline.extend(extra_params)

    cmdline += ['-define', 'thread-level=1']
    cmdline += ["-quality", str(quality), dst_jpegname]

    reporter.report_debug_info("imagemagick cmd line", cmdline)
    portable_popen(cmdline).wait()

def process_image_webp(
    ctx,
    source_image,
    dst_webpname,
    width=None,
    height=None,
    mode=None,
    quality=None,
    extra_params=None,
):
    reporter.report_debug_info("processing image:", dst_webpname)
    if width is None and height is None:
        raise ValueError("Must specify at least one of width or height.")

    im = find_imagemagick(ctx.build_state.config["IMAGEMAGICK_EXECUTABLE"])

    if quality is None:
        quality = get_quality(source_image)

    resize_key = ""
    if width is not None:
        resize_key += str(width)
    if height is not None:
        resize_key += "x" + str(height)

    cmdline = [im, source_image, "-auto-orient"]
    cmdline += ["-resize", resize_key]

    cmdline += ['-define', 'webp:lossless=false', '-define', 'thread-level=1']

    if extra_params:
        cmdline.extend(extra_params)

    cmdline += ["-quality", str(quality), dst_webpname]

    reporter.report_debug_info("imagemagick cmd line", cmdline)
    #print("imagemagick cmd line", cmdline)
    portable_popen(cmdline).wait()

@buildprogram(Image)
class ResizedImageBuildProgram(AttachmentBuildProgram):
    def build_artifact(self, artifact):
        ctx = get_ctx()
        plugin = ctx.env.plugins["image-resize"]
        config = plugin.config

        artifact.ensure_dir()
        AttachmentBuildProgram.build_artifact(self, artifact)

        if not config:
            return

        source_img = artifact.source_obj.attachment_filename

        with open(source_img, "rb") as f:
            _, w, h = get_image_info(f)

        # For every section in the config, we need to generate one image.
        for item, conf in config.items():
            width = int(conf["max_width"])
            height = int(conf.get("max_height", "0"))

            if not height:
                _, height = compute_dimensions(width, None, w, h)

            df = artifact.source_obj.url_path
            ext_pos = df.rfind(".")
            dst_jpegname = "%s-%s.jpg" % (df[:ext_pos], item)
            dst_webpname = "%s-%s.webp" % (df[:ext_pos], item)

            def closure(dst_jpegname, source_img, width, height, resize_image=True, ):
                # We need this closure, otherwise variables get updated and this
                # doesn't work at all.
                @ctx.sub_artifact(artifact_name=dst_jpegname, sources=[source_img])
                def build_thumbnail_artifact(artifact):
                    artifact.ensure_dir()
                    if not resize_image:
                        shutil.copy2(source_img, artifact.dst_jpegname)
                    else:
                        process_image(
                            ctx,
                            source_img,
                            artifact.dst_filename,
                            width,
                            height,
                            quality=89,
                            extra_params=[
                                "-strip",
                                "-interlace",
                                "Plane",
                            ],
                        )

            def webclosure(dst_webpname, source_img, width, height, resize_image=True, ):
                @ctx.sub_artifact(artifact_name=dst_webpname, sources=[source_img])
                def build_thumbnail_artifact(artifact):
                    artifact.ensure_dir()
                    process_image_webp(
                        ctx,
                        source_img,
                        artifact.dst_filename,
                        width,
                        height,
                        quality=89,
                        extra_params=[
                            "-strip",
                            "-interlace",
                            "Plane",
                        ],
                    )

            # If the image is larger than the max_width, resize it, otherwise
            # just copy it.
            resize_image = w > width or h > height
            closure(dst_jpegname, source_img, width, height, resize_image)
            webclosure(dst_webpname, source_img, width, height, resize_image)


class ImageResizePlugin(Plugin):
    name = u"thumbnail-generator"
    description = u"A configurable way to generate thumbnails."
    image_exts = ["jpg", "jpeg", "webp"]

    @cached_property
    def config(self):
        conf = self.get_config()
        return {section: conf.section_as_dict(section) for section in conf.sections()}
