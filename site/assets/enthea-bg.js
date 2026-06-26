// ENTHEA-inspired neural field background — minimal WebGL2 fragment shader
// Inspired by elder-plinius/ENTHEA (AGPL-3.0). This is a standalone lightweight excerpt.
// Renders at reduced resolution, caps FPS, respects prefers-reduced-motion.
(function () {
  "use strict";
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
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

  const SCALE = 0.25; // render at 25% resolution
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

  const FRAG = `#version 300 es
precision highp float;
in vec2 v;out vec4 o;
uniform float t;uniform vec2 r;

// --- simplex noise helpers ---
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

// domain-warped reaction-diffusion field
float field(vec2 p,float time){
  float n1=snoise(p*1.8+time*.06);
  float n2=snoise(p*2.5+vec2(n1*.4)+time*.04);
  float n3=snoise(p*3.2+vec2(n2*.3,n1*.2)+time*.03);
  // Wilson-Cowan-ish activation
  float activation=tanh(n1*.7+n2*.5+n3*.3);
  return activation;
}

void main(){
  vec2 uv=v;
  uv.x*=r.x/r.y;
  float f1=field(uv,t);
  float f2=field(uv+vec2(.3,.7),t+10.);
  // Klüver form constant mapping: tunnel-like radial gradient
  vec2 c=uv-vec2(r.x/r.y*.5,.5);
  float radius=length(c);
  float angle=atan(c.y,c.x);
  float tunnel=1./(1.+radius*2.5);
  // palette: deep indigo → teal → warm gold
  vec3 a=vec3(.05,.02,.15);
  vec3 b=vec3(.1,.25,.3);
  vec3 c_=vec3(.4,.3,.1);
  float mix1=tanh(f1*.6+.5);
  float mix2=tanh(f2*.5+.5);
  vec3 col=mix(a,b,mix1);
  col=mix(col,c_,mix2*.6);
  col+=tunnel*.08*vec3(.1,.15,.2);
  // subtle flicker
  col*=.92+.08*sin(t*.3);
  o=vec4(col,1);
}`;

  function compile(type, src) {
    const s = gl.createShader(type);
    gl.shaderSource(s, src);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      console.warn("ENTHEA bg shader:", gl.getShaderInfoLog(s));
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

  // fullscreen quad
  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,1,-1,-1,1,1,1]), gl.STATIC_DRAW);
  const loc = gl.getAttribLocation(prog, "p");
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  const uT = gl.getUniformLocation(prog, "t");
  const uR = gl.getUniformLocation(prog, "r");

  let frame = 0;
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
