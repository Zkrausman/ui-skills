# Selected SVG API

All imports are local ES modules; Node 20 or newer is sufficient. No npm install is needed. This is a code-authoring kit, not an untrusted-data format.

`kit/iso-kit.mjs` provides projection and ordinary solids:

- `iso([x,y,z], P)` projects a point; `P` has `origin: [sx,sy]`, `scale`, `azimuth` (default 45°), and `elevation` (default 30°).
- `boxCorners({x,y,w,d}, z0, z1)` returns world-space extremes for fitting.
- `slabOf({x,y,w,d,r}, z, height, P, steps=8, bevel=0)` returns fill, top, shade, crease, and outline paths for a rounded slab.
- `cylinder(cx,cy,radius,z,height,P,steps=32,bevel=0)` returns a vertical cylindrical solid.
- `solidSvg(paths,{tone,crease,halo,lit,flat,className,inner})` turns those paths into trusted SVG. Tone and crease are authored kit tokens such as `hi`, `mid`, `lo`, `faint`; `inner` is trusted markup.
- `lineSvg(d,{tone,...})`, `dotsSvg(points,{size,tone})`, `planOutline(plan,z,P)`, `topMatrix(at,z,P)`, and `faceTextSvg(transform,text,{size,tone,anchor})` add construction detail. Text is XML-escaped; raw paths and markup remain the caller's responsibility.
- `depthOf(point,P)` supports authored painter ordering. It does not resolve intersections.

`kit/asset.mjs` provides composition, palettes, and the final drop:

- `fitInto(points,{x,y,w,h},{pad=24,azimuth=45,elevation=30,...})` fits world-space points into a region. Regions and points must be finite and nondegenerate authored values.
- `assetSvg({width,height,label,body,paper,theme,accents,tint=0.6,weight,background=false,id})` returns one standalone SVG. Width/height must be positive finite values up to 8192. `label` is 1–500 XML-valid characters; `id` is a short identifier beginning with a letter. `body` is a trusted SVG string or array of strings. No arbitrary CSS or HTML-preview option is bundled.
- `groundTokens`, `accentTokens`, `accentCss`, and the OKLCH color helpers generate material ramps. Accent names use lowercase letters, digits, and hyphens; accent modes are `body` or `ink`.

`kit/lathe.mjs` provides round geometry on arbitrary axes: `frameAlong(origin,axis)`, `lathe(profile,frame,P,options)`, `disc(s0,s1,r,frame,P)`, `ringBand(s0,s1,rIn,rOut,frame,P)`, and `sphereOf(center,r,P)`. A profile is a list of axial-position/radius pairs. Supply sensible positive radii, bounded sample counts, and nonzero axes. These helpers do not validate arbitrary shapes.

`kit/tube.mjs` provides `tubePieces(points3,radius,P,options)` and `tubeSvg(piece,options)` for authored pipe runs. Draw the returned pieces in a deliberate depth order. Review the module's function definitions for advanced geometry arguments rather than inventing unsupported options.

Only local imports are supported. The retained modules perform geometry/string construction and do not write files or launch programs. The one template is the explicit file-writing entrypoint and refuses an existing output directory. No HTML, PNG, browser capture, WebGL, React, or network demos are bundled.
