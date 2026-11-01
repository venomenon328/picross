shader_type spatial;
render_mode unshaded, cull_disabled;
#include "res://study/book/fold.gdshaderinc"
uniform sampler2D leather_source : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D table_source : source_color, filter_linear_mipmap, repeat_disable;
uniform vec4 base_color : source_color = vec4(1.0);
uniform float kind = 0.0;
varying vec3 surface;
varying vec3 surface_normal;
void vertex() { surface=VERTEX; surface_normal=NORMAL; }
void fragment() {
    vec3 n=normalize(surface_normal);
    float light=0.68+0.32*max(0.0,dot(n,normalize(vec3(-0.35,0.6,1.0))));
    if (kind<0.5) {
        // Independent leather: no silhouette, cloth or shadows in its UVs.
        vec3 leather=texture(leather_source,surface.xy*0.22).rgb;
        float rim=max(smoothstep(10.16,10.43,abs(surface.x)),smoothstep(6.33,6.55,abs(surface.y)));
        float joint=1.0-smoothstep(0.60,0.75,abs(surface.x));
        light=mix(light,0.44+0.56*max(0.0,dot(n,normalize(vec3(-0.35,0.6,1.0)))),joint);
        ALBEDO=leather*(0.75+rim*0.28)*light;
    } else if (kind<1.5) {
        float crown=fold_profile(abs(surface.x)).x;
        float depth=(crown-surface.z)/(crown+0.436-hinge_height(surface.x));
        // Six subtle signatures; smoothly average subpixel layers instead of
        // thresholding aliased stripes into diagonal patches at 1080p.
        float phase=depth*6.0;
        float resolved=1.0-smoothstep(0.25,0.65,fwidth(phase));
        float separation=(0.5+0.5*cos(phase*6.283185))*resolved;
        float contact=0.87+0.13*smoothstep(0.0,0.06,depth);
        ALBEDO=base_color.rgb*light*contact*(1.0-0.15*separation);
    } else if (kind<2.5) {
        // One non-tiling photograph on stationary world geometry. Its aspect
        // ratio is preserved while the same camera moves over book and table.
        vec3 table=texture(table_source,vec2(surface.x/48.0+0.5,0.5-surface.y/32.0)).rgb;
        vec2 outside=abs(surface.xy-vec2(0.10,-0.10))-vec2(10.26,6.38);
        float edge=length(max(outside,vec2(0.0)))+min(max(outside.x,outside.y),0.0)-0.17;
        float shadow=0.46+0.54*smoothstep(0.0,0.45,edge);
        ALBEDO=table*shadow;
    } else {
        ALBEDO=base_color.rgb*light;
    }
}
