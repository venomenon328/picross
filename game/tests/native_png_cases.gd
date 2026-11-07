extends RefCounted
const PNG = preload("res://tests/native_png.gd")

static func run(t: SceneTree) -> void:
	# Vary the last alpha byte through its entire range, including almost opaque.
	# Decode the real PNG buffer, not a mock of the conversion or writer.
	for alpha: int in range(256):
		var pixels := PackedByteArray([17,29,53,255,71,97,113,255,131,149,173,alpha])
		var source := Image.create_from_data(3,1,false,Image.FORMAT_RGBA8,pixels)
		var encoded: Image = PNG.exact_image(source)
		var decoded := Image.new()
		t.check(decoded.load_png_from_buffer(encoded.save_png_to_buffer()) == OK,"PNG actual decoder accepts evidence")
		decoded.convert(Image.FORMAT_RGBA8)
		t.check(decoded.get_size() == source.get_size() and decoded.get_data() == pixels,"PNG all alpha bytes and RGB pixels survive")
		t.check(source.get_format() == Image.FORMAT_RGBA8 and source.get_data() == pixels,"PNG measured readback remains unchanged")
		t.check(encoded.get_format() == (Image.FORMAT_RGB8 if alpha == 255 else Image.FORMAT_RGBA8),"PNG only exact opacity uses RGB")
	for format: Image.Format in [Image.FORMAT_RGB8,Image.FORMAT_L8,Image.FORMAT_RGBAF]:
		var other := Image.create(2,2,false,format)
		t.check(PNG.exact_image(other) == other,"PNG preserves other native formats")
	var mipmapped := Image.create(2,2,true,Image.FORMAT_RGBA8)
	t.check(PNG.exact_image(mipmapped) == mipmapped,"PNG preserves mipmapped inputs")
