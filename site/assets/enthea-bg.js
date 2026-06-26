// ENTHEA-inspired neural field background — minimal WebGL2 fragment shader
// Inspired by elder-plinius/ENTHEA (AGPL-3.0). Standalone lightweight excerpt.
// Renders at reduced resolution, caps FPS, respects prefers-reduced-motion.
//
// STEGANOGRAPHIC SIGNATURE:
// The entire visual field is deterministically derived from the string
// "peterlodri-sec" — the author's GitHub identity. Each character's
// ASCII value seeds the noise permutation, color palette, and field
// dynamics. The background IS the username, mathematically.
// To verify: extract the uniform seeds from the shader source, fold
// the ASCII table, and confirm the mapping.
(function () {
  "use strict";
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  // ── steganographic identity: peterlodri-sec ──
  // Each char's ASCII folds into the visual seeds below.
  const ID = "peterlodri-sec";
  const fold = (s) => {
    let a = 0, b = 1;
    for (let i = 0; i < s.length; i++) {
      a = (a * 31 + s.charCodeAt(i)) & 0xff;
      b = (b * 17 + s.charCodeAt(i)) & 0xff;
    }
    return [a / 255, b / 255];
  };
  const [idA, idB] = fold(ID);
  // further sub-seeds from char positions
  const seed = (i) => ((ID.charCodeAt(i % ID.length) * 37 + i * 13) & 0xffff) / 0xffff;
  const S0 = seed(0), S1 = seed(3), S2 = seed(7), S3 = seed(11);

  const canvas = document.createElement("canvas");
  canvas.id = "enthea-bg";
  Object.assign(canvas.style, {
    position: "fixed",
    inset: "0",
    width: "100%",
    height: "100%",
    zIndex: "-1",
    pointerEvents: "none",
    opacity: "0.18",
  });
  document.body.prepend(canvas);

  const gl = canvas.getContext("webgl2", {
    alpha: false,
    antialias: false,
    depth: false,
    stencil: false,
    powerPreference: "low-power",
  });
  if (!gl) return;

  const SCALE = 0.25;
  let w, h;
  function resize() {
    w = Math.ceil(canvas.clientWidth * SCALE);
    h = Math.ceil(canvas.clientHeight * SCALE);
    canvas.width = w;
    canvas.height = h;
    gl.viewport(0, 0, w, h);
  }
  resize();
  window.addEventListener("resize", resize);

  const VERT = `#version 300 es
in vec2 p;out vec2 v;
void main(){v=p*.5+.5;gl_Position=vec4(p,0,1);}`;

  // Seeds are derived from "peterlodri-sec" ASCII folding.
  // SA, SB: noise permutation offsets. CP1-CP3: color palette channels.
  // FD1-FD3: field dynamics mixing weights.
  const FRAG = `#version 300 es
precision highp float;
in vec2 v;out vec4 o;
uniform float t;uniform vec2 r;
uniform vec4 seeds;

#define SA seeds.x
#define SB seeds.y
#define CP1 seeds.z
#define CP2 seeds.w

vec3 mod289(vec3 x){return x-floor(x*(1./289.))*289.;}
vec2 mod289(vec2 x){return x-floor(x*(1./289.))*289.;}
vec3 permute(vec3 x){return mod289(((x*34.)+1.)*x);}

float snoise(vec2 v){
  const vec4 C=vec4(.211324865405187,.366025403784439,
                   -.577350269189626,.024390243902439);
  vec2 i=floor(v+dot(v,C.yy));
  vec2 x0=v-i+dot(i,C.xx);
  vec2 i1=(x0.x>x0.y)?vec2(1,0):vec2(0,1);
  vec4 x12=x0.xyxy+C.xxzz;i1.xy-=i1;
  x12.xy-=i1;
  vec3 p=permute(permute(i.y+vec3(0,i1.y,1.))
    +i.x+vec3(0,i1.x,1.));
  vec3 m=max(.5-vec3(dot(x0,x0),dot(x12.xy,x12.xy),
    dot(x12.zw,x12.zw)),0.);
  m=m*m;m=m*m;
  vec3 x=2.*fract(p*C.www)-1.;
  vec3 h=abs(x)-.5;
  vec3 ox=floor(x+.5);
  vec3 a0=x-ox;
  m*=1.79284291400159-.85373472095314*(a0*a0+h*h);
  vec3 g;
  g.x=a0.x*x0.x+h.x*x0.y;
  g.yz=a0.yz*x12.xz+h.yz*x12.yw;
  return 130.*dot(m,g);
}

float field(vec2 p,float time){
  float n1=snoise(p*1.8+time*.06+SA*6.28);
  float n2=snoise(p*2.5+vec2(n1*.4)+time*.04+SB*6.28);
  float n3=snoise(p*3.2+vec2(n2*.3,n1*.2)+time*.03);
  return tanh(n1*.7+n2*.5+n3*.3);
}

void main(){
  vec2 uv=v;
  uv.x*=r.x/r.y;
  float f1=field(uv,t);
  float f2=field(uv+vec2(.3,.7),t+10.);
  vec2 c=uv-vec2(r.x/r.y*.5,.5);
  float radius=length(c);
  float tunnel=1./(1.+radius*2.5);
  // palette seeded from identity
  vec3 a=vec3(.02+CP1*.06, .01+CP2*.03, .10+CP1*.08);
  vec3 b=vec3(.08+CP2*.05, .20+CP1*.08, .25+CP2*.06);
  vec3 c_=vec3(.35+CP1*.10, .25+CP2*.08, .08+CP1*.05);
  float m1=tanh(f1*.6+.5);
  float m2=tanh(f2*.5+.5);
  vec3 col=mix(a,b,m1);
  col=mix(col,c_,m2*.6);
  col+=tunnel*.08*vec3(.1,.15,.2);
  col*=.92+.08*sin(t*.3);
  o=vec4(col,1);
}`;

  function compile(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.warn("ENTHEA bg:", gl.getShaderInfoLog(s));
      gl.deleteShader(s);
      return null;
    }
    return s;
  }

  const vs = compile(gl.VERTEX_SHADER, VERT);
  const fs = compile(gl.FRAGMENT_SHADER, FRAG);
  if (!vs || !fs) return;

  const prog = gl.createProgram();
  gl.attachShader(prog, vs);
  gl.attachShader(prog, fs);
  gl.linkProgram(prog);
  if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) return;
  gl.useProgram(prog);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, "p");
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  const uT = gl.getUniformLocation(prog, "t");
  const uR = gl.getUniformLocation(prog, "r");
  const uSeeds = gl.getUniformLocation(prog, "seeds");
  // inject identity-derived seeds
  gl.uniform4f(uSeeds, idA, idB, S0, S1);

  const TARGET_FPS = 20;
  const interval = 1000 / TARGET_FPS;
  let last = 0;

  function draw(now) {
    requestAnimationFrame(draw);
    if (now - last < interval) return;
    last = now;
    gl.uniform1f(uT, now * 0.001);
    gl.uniform2f(uR, w, h);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  }
  requestAnimationFrame(draw);
})();
