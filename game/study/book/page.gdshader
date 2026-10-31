shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, depth_draw_opaque;
uniform sampler2D material_source : source_color, filter_linear_mipmap, repeat_disable;
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
void vertex() {
	float d = VERTEX.x;
	original = vec2(side*d, VERTEX.y);
	angle = turn*3.14159265;
	float curl = sin(UV.x*3.14159265)*sin(angle)*0.65;
	VERTEX.x = side*(d*cos(angle)+curl*sin(angle));
	VERTEX.z += d*sin(angle)-curl*cos(angle) + lift*sin(UV.x*3.14159265);
	NORMAL = vec3(-side*sin(angle), 0.0, cos(angle));
}
void fragment() {
	// Only the UI-free original material is sampled; its bytes remain unchanged.
	vec2 material_uv = vec2(mix(0.96, 0.029, UV.x), mix(0.035, 0.965, UV.y));
	vec3 paper = texture(material_source, material_uv).rgb;
	float edge = min(UV.x, min(UV.y, 1.0-UV.y));
	paper *= 1.0 - 0.10*exp(-edge*120.0);
	float gutter = 0.21*exp(-UV.x*35.0);
	float cast_shadow = shadow*exp(-pow((UV.x-0.10-shadow*0.35)*4.2, 2.0));
	float lighting = 1.0 - gutter - 0.18*sin(turn*3.14159265) - 0.20*cast_shadow;
	bool front = side > 0.0 ? FRONT_FACING : !FRONT_FACING;
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
