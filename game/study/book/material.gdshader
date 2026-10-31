shader_type spatial;
render_mode unshaded, cull_back;
uniform sampler2D material_source : source_color, filter_linear_mipmap, repeat_disable;
uniform vec4 base_color : source_color = vec4(0.12, 0.105, 0.085, 1.0);
uniform float kind = 0.0;
varying vec3 surface_position;
float noise(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
void vertex() { surface_position = VERTEX; }
void fragment() {
	float n = noise(floor(UV * 1500.0));
	float grain = 0.0;
	if (kind < 0.5) {
		grain = (n - 0.5) * 0.015;
	} else if (kind < 1.5) {
		grain = sin(UV.y * 1900.0 + sin(UV.x * 47.0) * 0.8) * 0.035; // page edges
	} else {
		grain = sin(surface_position.x * 19.0 + sin(surface_position.y * 0.9) * 0.4) * 0.012 + (n-0.5)*0.008;
	}
	ALBEDO = base_color.rgb + grain;
	if (kind < 0.5) {
		// The paper mesh covers the centre; the exposed original perimeter
		// supplies leather creases and worn corners at their actual proportions.
		ALBEDO = texture(material_source, vec2(mix(0.012,0.978,UV.x),mix(0.018,0.984,UV.y))).rgb * 0.84;
	}
	if (kind > 1.5) {
		ALBEDO = texture(material_source,vec2(UV.x,mix(0.001,0.017,UV.y))).rgb*0.48;
		vec2 outside = abs(surface_position.xy - vec2(0.12, -0.18)) - vec2(10.45, 6.52);
		float edge = length(max(outside, vec2(0.0))) + min(max(outside.x, outside.y), 0.0);
		ALBEDO *= 0.4 + 0.6 * smoothstep(0.0, 0.55, edge);
	}
	ROUGHNESS = kind < 0.5 ? 0.72 : 0.94;
	SPECULAR = 0.2;
	NORMAL_MAP = vec3(0.5 + (n-0.5)*0.08, 0.5, 1.0);
}
