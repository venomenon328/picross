shader_type canvas_item;
render_mode unshaded;

uniform int overlap_mode = 0;
uniform vec4 grid;
uniform vec4 row_clues;
uniform vec4 column_clues;
uniform vec4 protected_areas[24];
uniform int protected_count = 0;
uniform vec2 canvas_pixels;
uniform float opacity = 0.48;
varying vec2 page_pixel;

bool inside(vec2 p, vec4 r) {
	return r.z > 0.0 && r.w > 0.0 && all(greaterThanEqual(p, r.xy)) && all(lessThan(p, r.xy + r.zw));
}

float outside_distance(vec2 p, vec4 r) {
	return length(max(abs(p - (r.xy + r.zw * 0.5)) - r.zw * 0.5, vec2(0.0)));
}

void vertex() {
	page_pixel = VERTEX;
}

void fragment() {
	vec4 ink = texture(TEXTURE, UV);
	if (inside(page_pixel, grid) || inside(page_pixel, row_clues) || inside(page_pixel, column_clues)) {
		if (overlap_mode == 1) {
			ink.a *= 0.20;
		} else if (overlap_mode == 2) {
			// Only decoration is sampled. No screen texture, functional UI or
			// additional render target. Premultiplied averaging avoids alpha halos.
			vec2 d = vec2(2.5) / max(canvas_pixels, vec2(1.0));
			vec4 sum = vec4(0.0);
			for (int y = -1; y <= 1; y++) {
				for (int x = -1; x <= 1; x++) {
					vec2 uv = clamp(UV + d * vec2(float(x), float(y)), vec2(0.0), vec2(1.0));
					vec4 c = texture(TEXTURE, uv);
					float weight = (x == 0 ? 2.0 : 1.0) * (y == 0 ? 2.0 : 1.0);
					sum += vec4(c.rgb * c.a, c.a) * weight;
				}
			}
			sum /= 16.0;
			ink = vec4(sum.rgb / max(sum.a, 0.00001), sum.a);
		} else if (overlap_mode == 3) {
			ink.a = 0.0;
		}
	}
	// Actual controls retain protection with a soft eight-display-pixel approach.
	// Clues follow the grid's A/B1/B2/C treatment; no independent opaque mask.
	for (int i = 0; i < protected_count; i++) {
		vec4 r = protected_areas[i];
		if (r.z > 0.0 && r.w > 0.0) {
			ink.a *= smoothstep(0.0, 8.0, outside_distance(page_pixel, r));
		}
	}
	// All sources share a 3:1 contain fit inside the physical 4:1 canvas.
	// Fade at that common source perimeter, including transparent side padding;
	// no per-image mask, crop, offset or hard edge is introduced.
	vec2 art_uv = vec2((UV.x - 0.125) / 0.75, UV.y);
	float edge = min(min(art_uv.x, 1.0 - art_uv.x), min(art_uv.y, 1.0 - art_uv.y));
	ink.a *= smoothstep(0.0, 0.035, edge);
	COLOR = vec4(ink.rgb, ink.a * opacity);
}
