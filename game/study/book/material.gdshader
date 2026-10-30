shader_type spatial;
render_mode cull_back;
uniform vec4 base_color : source_color = vec4(0.12, 0.105, 0.085, 1.0);
uniform float kind = 0.0;
varying vec3 surface_position;
float noise(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void vertex() { surface_position = VERTEX; }
void fragment() {
	float n = noise(floor(UV * 1500.0));
	float grain = 0.0;
	if (kind < 0.5) {
		grain = (n - 0.5) * 0.045; // fine leather pores
	} else if (kind < 1.5) {
		grain = sin(UV.y * 1900.0 + sin(UV.x * 47.0) * 0.8) * 0.035; // page edges
	} else {
		grain = sin(surface_position.x * 19.0 + sin(surface_position.y * 0.9) * 0.4) * 0.012 + (n-0.5)*0.008;
	}
	ALBEDO = base_color.rgb + grain;
	if (kind > 1.5) {
		vec2 outside = abs(surface_position.xy - vec2(0.10, -0.15)) - vec2(9.39, 5.28);
		float edge = length(max(outside, vec2(0.0))) + min(max(outside.x, outside.y), 0.0);
		ALBEDO *= 0.62 + 0.38 * smoothstep(-0.03, 0.32, edge);
	}
	ROUGHNESS = kind < 0.5 ? 0.72 : 0.94;
	SPECULAR = 0.2;
	NORMAL_MAP = vec3(0.5 + (n-0.5)*0.08, 0.5, 1.0);
}
