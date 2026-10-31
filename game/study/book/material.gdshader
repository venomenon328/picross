shader_type spatial;
render_mode unshaded, cull_disabled;
uniform sampler2D leather_source : source_color, filter_linear_mipmap, repeat_enable;
uniform vec4 base_color : source_color = vec4(1.0);
uniform float kind = 0.0;
varying vec3 surface;
varying vec3 surface_normal;
float noise(vec2 p) { return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453); }
void vertex() { surface=VERTEX; surface_normal=NORMAL; }
void fragment() {
    vec3 n=normalize(surface_normal);
    float light=0.68+0.32*max(0.0,dot(n,normalize(vec3(-0.35,0.6,1.0))));
    if (kind<0.5) {
        // Independent leather: no silhouette, cloth or shadows in its UVs.
        vec3 leather=texture(leather_source,surface.xy*0.22).rgb;
        float rim=max(smoothstep(10.16,10.43,abs(surface.x)),smoothstep(6.33,6.55,abs(surface.y)));
        ALBEDO=leather*(0.75+rim*0.28)*light;
    } else if (kind<1.5) {
        float crown=0.26*pow(1.0-clamp(abs(surface.x)/0.75,0.0,1.0),3.0);
        float depth=(crown-surface.z)/(0.43+crown*0.35);
        // Six subtle signatures; smoothly average subpixel layers instead of
        // thresholding aliased stripes into diagonal patches at 1080p.
        float phase=depth*6.0;
        float resolved=1.0-smoothstep(0.25,0.65,fwidth(phase));
        float separation=(0.5+0.5*cos(phase*6.283185))*resolved;
        float contact=0.87+0.13*smoothstep(0.0,0.06,depth);
        ALBEDO=base_color.rgb*light*contact*(1.0-0.15*separation);
    } else if (kind<2.5) {
        // Continuous woven support; world-space contact follows the cover.
        float weave=sin(surface.x*260.0)*sin(surface.y*260.0)*0.008;
        vec2 outside=abs(surface.xy-vec2(0.10,-0.10))-vec2(10.26,6.38);
        float edge=length(max(outside,vec2(0.0)))+min(max(outside.x,outside.y),0.0)-0.17;
        float shadow=0.46+0.54*smoothstep(0.0,0.45,edge);
        ALBEDO=(base_color.rgb+weave+(noise(floor(surface.xy*180.0))-0.5)*0.008)*shadow;
    } else {
        ALBEDO=base_color.rgb*light;
    }
}
