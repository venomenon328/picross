shader_type canvas_item;
render_mode unshaded;

uniform int overlap_mode = 0;
uniform vec4 grid;
uniform vec4 protected_areas[24];
uniform int protected_count = 0;
uniform vec2 canvas_pixels;
uniform float opacity = 0.48;
varying vec2 page_pixel;

bool inside(vec2 p, vec4 r) {
	return r.z > 0.0 && r.w > 0.0 && all(greaterThanEqual(p, r.xy)) && all(lessThan(p, r.xy + r.zw));
}

vec4 premultiplied(sampler2D source, vec2 uv) {
	vec4 c = texture(source, clamp(uv, vec2(0.0), vec2(1.0)));
	return vec4(c.rgb * c.a, c.a);
}

void vertex() {
	page_pixel = VERTEX;
}

void fragment() {
	vec4 ink = texture(TEXTURE, UV);
	if (inside(page_pixel, grid)) {
		if (overlap_mode == 1) {
			ink.a *= 0.20;
		} else if (overlap_mode == 2) {
			// Only decoration is sampled. No screen texture, functional UI or
			// additional render target. Premultiplied averaging avoids alpha halos.
			vec2 d = vec2(2.5) / max(canvas_pixels, vec2(1.0));
			vec4 sum = premultiplied(TEXTURE, UV) * 4.0;
			sum += premultiplied(TEXTURE, UV + vec2(d.x, 0.0)) * 2.0;
			sum += premultiplied(TEXTURE, UV - vec2(d.x, 0.0)) * 2.0;
			sum += premultiplied(TEXTURE, UV + vec2(0.0, d.y)) * 2.0;
			sum += premultiplied(TEXTURE, UV - vec2(0.0, d.y)) * 2.0;
			sum += premultiplied(TEXTURE, UV + d);
			sum += premultiplied(TEXTURE, UV - d);
			sum += premultiplied(TEXTURE, UV + vec2(d.x, -d.y));
			sum += premultiplied(TEXTURE, UV + vec2(-d.x, d.y));
			sum /= 16.0;
			ink = vec4(sum.rgb / max(sum.a, 0.00001), sum.a);
		} else if (overlap_mode == 3) {
			ink.a = 0.0;
		}
	}
	// Same local clue/control protection in every comparison. These rectangles
	// come from real geometry and never depend on artwork or solution cells.
	for (int i = 0; i < protected_count; i++) {
		if (inside(page_pixel, protected_areas[i])) { ink.a = 0.0; }
	}
	COLOR = vec4(ink.rgb, ink.a * opacity);
}
