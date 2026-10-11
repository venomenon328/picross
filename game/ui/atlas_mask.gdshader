shader_type canvas_item;
render_mode unshaded;
// PERF-A coefficients; per-command color replaces the probe's uniform material.
varying vec4 ink;
void vertex() {
	ink = COLOR;
}
void fragment() {
	vec4 mask = texture(TEXTURE, UV);
	COLOR = vec4(ink.rgb * mask.r + vec3(mask.g), mask.a * ink.a);
}
