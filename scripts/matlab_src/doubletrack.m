function result = doubletrack(params, wl, pol, guess)
% INPUT PARAMETERS:
% 
% params - waveguide parameters struct with the fields:
%   dn_track - refractive index modification in tracks
%   dn_halo - refractive index modification in halos
%   track_w - track width
%   track_h - track height
%   gap - gap between the tracks
%   space_x, space_y - space to add from the waveguide to the mesh boundaries
%   dx, dy - mesh step
%   npml - number of PML layers
%   nmodes - number of modes to calculate
% wl - wavelength
% pol - polarization (1 for x, 2 for y)
% guess - (optional) initial guess for effective index
if ~(pol == 1 || pol == 2)
    error("Invalid polarization");
end
dn_track = double(params.dn_track);
dn_halo = double(params.dn_halo);
track_w = double(params.track_w);
track_h = double(params.track_h);
gap = double(params.gap);
space_x = double(params.space_x);
if isfield(params, "space_y")
    space_y = double(params.space_y);
else
    space_y = space_x;
end
dx = double(params.dx);
if isfield(params, "dy")
    dy = double(params.dy);
else
    dy = dx;
end
npml = params.npml;
%% Calculate mode
xmax = (gap+track_w)/2 + space_x;
xmin = 0;
ymax = track_h/2 + space_y;
ymin = 0;
x = (xmin:dx:xmax)';
xc = x(1:end-1) + dx / 2;
y = (ymin:dy:ymax);
yc = y(1:end-1) + dy / 2;
[xxc, yyc] = meshgrid(xc, yc);
ax = [2 3 1];  % Crystal orientation
n_background = zeros(3, 1);
for i=1:length(ax)
    n_background(i) = sqrt(epsKTPkato(wl, ax(i)));
end
[epsxx,epsyy,epszz] = meshdoubletrack(xxc,yyc,n_background,dn_track,dn_halo,track_w,track_h,gap);
% Complex coordinate stretching (PML):
[xpml,ypml] = stretchmesh(x,y,[npml,0,npml,0],1+1i*2);
dxpml = diff(xpml);
dypml = diff(ypml);
boundary = '0000';
if pol == 1
    boundary([2 4]) = 'A';
else
    boundary([2 4]) = 'S';
end
if ~exist('guess', 'var')
    if pol == 1
        eps = epsxx;
    else
        eps = epsyy;
    end
    guess = sqrt(max(max(eps)));
end
if ~isfield(params, 'nmodes')
    params.nmodes = 1;
end
[Hx,Hy,neff] = wgmodes(wl,guess,params.nmodes,dxpml,dypml,epsxx,epsyy,epszz,boundary);
if pol == 1
    [maxHy, iFund] = max(abs(Hy(1,1,:)));
else
    [maxHx, iFund] = max(abs(Hx(1,1,:)));
end
neff = neff(iFund);
Hx = Hx(:,:,iFund);
Hy = Hy(:,:,iFund);
[x,y,Hx,Hy] = extrapolate(x,y,Hx,Hy,boundary);
[xc,yc,epsxx,epsyy,epszz] = extrapolate(xc,yc,epsxx,epsyy,epszz,boundary);
dx = diff(x); dy = diff(y);
[Hz,Ex,Ey,Ez] = postprocess(wl,neff,Hx,Hy,dx,dy,epsxx,epsyy,epszz,boundary);
result.x = x; result.y = y; result.xc = xc; result.yc = yc;
result.epsxx = epsxx; result.epsyy = epsyy; result.epszz = epszz;
result.neff = neff;
result.Hx = Hx; result.Hy = Hy; result.Hz = Hz;
result.Ex = Ex; result.Ey = Ey; result.Ez = Ez;
end
