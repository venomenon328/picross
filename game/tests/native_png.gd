extends RefCounted
## Lossless encoding of native evidence; never mutate the measured readback.

static func exact_image(image: Image) -> Image:
	if image.get_format() != Image.FORMAT_RGBA8 or image.has_mipmaps():
		return image
	# detect_alpha() rounds alpha 254 to opaque. A byte-exact roundtrip also
	# covers the last pixel and retains every non-255 alpha without a script loop.
	var encoded: Image = image.duplicate()
	encoded.convert(Image.FORMAT_RGB8)
	var restored: Image = encoded.duplicate()
	restored.convert(Image.FORMAT_RGBA8)
	return encoded if restored.get_data() == image.get_data() else image

static func write(image: Image, path: String) -> int:
	return exact_image(image).save_png(path)
