shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, depth_draw_opaque;
#include "res://book/fold.gdshaderinc"
uniform sampler2D paper_source : source_color, filter_linear_mipmap, repeat_disable;
uniform vec2 paper_offset = vec2(0.0);
uniform vec2 back_paper_offset = vec2(0.0);
uniform sampler2D content : source_color, filter_linear, repeat_disable;
uniform sampler2D back_content : source_color, filter_linear, repeat_disable;
uniform bool has_content = false;
uniform bool has_back = false;
uniform vec4 content_rect = vec4(-11.9111, -6.7, 23.8222, 13.4);
uniform vec4 back_rect = vec4(-11.9111, -6.7, 23.8222, 13.4);
uniform float side = 1.0;
uniform float turn = 0.0;
uniform float shadow = 0.0;
uniform float lift = 0.0;
varying vec2 original;
varying float angle;
varying vec3 paper_normal;
void vertex() {
	float d = VERTEX.x;
	original = vec2(side*d, VERTEX.y);
	// Keep the valley attached while the shoulder bends above the resting block.
	// In both landing poses the same crown supports the sheet, without inversion.
	float t = clamp(d/0.75,0.0,1.0);
	vec2 fold = fold_profile(d);
	VERTEX.y *= 1.0-0.004*fold.x/0.22;
	angle = turn*3.14159265;
	float curl = sin(UV.x*3.14159265)*sin(angle)*0.65;
	float curl_slope = cos(UV.x*3.14159265)*3.14159265/10.0*sin(angle)*0.65;
	float dx = (1.0-0.008*(1.0-t)/0.75)*cos(angle)+curl_slope*sin(angle);
	float dz = sin(angle)+fold.y-curl_slope*cos(angle)+lift*3.14159265/10.0*cos(UV.x*3.14159265);
	VERTEX.x = side*((d+0.004*pow(1.0-t,2.0))*cos(angle)+curl*sin(angle));
	VERTEX.z += d*sin(angle)+fold.x-curl*cos(angle)+lift*sin(UV.x*3.14159265);
	paper_normal = normalize(vec3(-side*dz,0.0,dx));
	NORMAL = paper_normal;
}
void fragment() {
	// One original bitmap, stable crops per logical page, no mirroring/randomness.
	bool front = side > 0.0 ? FRONT_FACING : !FRONT_FACING;
	vec3 paper = mix(texture(paper_source,UV*0.72+(front ? paper_offset : back_paper_offset)).rgb,vec3(1.0,0.98,0.93),0.55);
	float edge = min(min(UV.x,1.0-UV.x), min(UV.y, 1.0-UV.y));
	paper *= 1.0 - 0.10*exp(-edge*120.0);
	vec3 normal = normalize(paper_normal)*(front ? 1.0 : -1.0);
	float curvature_light = 0.78+0.22*dot(normal,normalize(vec3(-0.5,0.25,1.0)));
	// Local occlusion between the two actual rising shoulders, not a UI overlay.
	curvature_light *= 1.0-0.20*(1.0-smoothstep(0.0,0.20,abs(original.x)));
	float cast_shadow = shadow*exp(-pow((UV.x-0.10-shadow*0.35)*4.2, 2.0));
	float lighting = curvature_light - 0.18*sin(turn*3.14159265) - 0.20*cast_shadow;
	vec2 location = front ? original : vec2(-original.x, original.y);
	vec4 region = front ? content_rect : back_rect;
	vec2 ink_uv = vec2((location.x-region.x)/region.z, 1.0-(location.y-region.y)/region.w);
	bool inside = all(greaterThanEqual(ink_uv, vec2(0.0))) && all(lessThanEqual(ink_uv, vec2(1.0)));
	vec4 ink = vec4(0.0);
	if (inside && front && has_content) { ink = texture(content, ink_uv); }
	if (inside && !front && has_back) { ink = texture(back_content, ink_uv); }
	// Premultiplied viewport colors: do not multiply their AA edges twice.
	ALBEDO = paper*lighting*(1.0-ink.a) + ink.rgb;
}
