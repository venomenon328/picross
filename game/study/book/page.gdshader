shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled, depth_draw_opaque;
uniform sampler2D content : source_color, filter_linear, repeat_disable;
uniform bool has_content = false;
uniform float turn = 0.0;
uniform float shadow = 0.0;
varying float bend;

float grain(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}
void vertex() {
	float distance_to_binding = 9.12 - VERTEX.x;
	bend = turn * 3.14159265 + sin(UV.x * 3.14159265) * sin(turn * 3.14159265) * 0.34;
	VERTEX.x = 9.12 - distance_to_binding * cos(bend);
	VERTEX.z += distance_to_binding * sin(bend);
	NORMAL = vec3(-sin(bend), 0.0, cos(bend));
}
void fragment() {
	// Calm material on the used page; grain and edge wear never recolor UI ink.
	float edge = min(min(UV.x - 0.026, 0.974 - UV.x), min(UV.y - 0.024, 0.966 - UV.y));
	vec3 paper = vec3(0.947, 0.915, 0.846);
	paper += (grain(floor(UV * vec2(3072.0, 1728.0))) - 0.5) * 0.009;
	paper -= vec3(0.055, 0.047, 0.032) * exp(-max(edge, 0.0) * 170.0);
	vec4 ink = has_content && FRONT_FACING ? texture(content, UV) : vec4(0.0);
	bool outside = edge < 0.0;
	if (outside && ink.a < 0.001) { discard; }
	float light = 1.0 - 0.23 * sin(turn * 3.14159265);
	// Transparent 2D viewport colors are premultiplied. Multiplying them by
	// alpha again would darken antialiased text/grid edges at the handoff.
	vec3 color = outside ? ink.rgb / max(ink.a, 0.001) : paper * (1.0 - ink.a) + ink.rgb;
	float page_shadow = shadow * exp(-pow((UV.x - 0.75 + shadow * 0.42) * 8.0, 2.0));
	ALBEDO = color * light * (1.0 - 0.18 * page_shadow);
	ALPHA = outside ? ink.a : 1.0;
}
