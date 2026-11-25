#!/usr/bin/env python3
from stepup.core.api import static
from stepup.report.api import cat_pdf, raster_pdf

static("smile.pdf")
raster_pdf("smile.pdf", "rastered/")
raster_pdf("smile.pdf", "rastered/smile.png", resolution=50)
cat_pdf(["smile.pdf", "smile.pdf"], "double.pdf")
raster_pdf("double.pdf", "rastered/double-{0p}-{t}.png", resolution=50)
