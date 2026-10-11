shader_type canvas_item;
render_mode unshaded;
uniform vec4 base_color : source_color = vec4(1.0);
uniform float opacity = 1.0;
varying float vertex_alpha;
void vertex() {
	vertex_alpha = COLOR.a;
}
void fragment() {
	vec4 mask = texture(TEXTURE, UV);
	COLOR = vec4(base_color.rgb * mask.r + vec3(mask.g), mask.a * opacity * base_color.a * vertex_alpha);
}
