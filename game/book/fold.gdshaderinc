// The bound fold occupies only the existing 0.75-unit UI exclusion strip.
// Height and its derivative: a joined valley, a round shoulder, then flat paper.
vec2 fold_profile(float d) {
	float t = clamp(d / 0.28, 0.0, 1.0);
	if (d < 0.28) {
		return vec2(0.22*t*t*(3.0-2.0*t), 0.22*6.0*t*(1.0-t)/0.28);
	}
	t = clamp((d-0.28)/0.47, 0.0, 1.0);
	return vec2(0.22*(1.0-t*t*(3.0-2.0*t)), -0.22*6.0*t*(1.0-t)/0.47);
}

// The cover itself rises into the spine, with recessed flexible joints.
float hinge_height(float x) {
	x = abs(x);
	if (x < 0.16) return mix(0.25,0.20,smoothstep(0.0,0.16,x));
	if (x < 0.30) return mix(0.20,0.02,smoothstep(0.16,0.30,x));
	if (x < 0.42) return mix(0.02,-0.06,smoothstep(0.30,0.42,x));
	if (x < 0.60) return mix(-0.06,-0.01,smoothstep(0.42,0.60,x));
	return mix(-0.01,0.0,smoothstep(0.60,0.75,x));
}
