xmax = width / 2 + space_x;
dy = dx;
%% Calculate signal mode
wl_signal = wl_pump * 2;
[x_s,y_s,xc,yc,nx,ny,epsxx_s,epsyy_s,epszz_s] = meshfiorentino(dn,width,wl_signal,xmax,ymin,ymax,dx,dy);
%guess = sqrt(max(max(epsxx)));
guess = 1.769769200250290;
nmodes = 1;
boundary_s = '0000';
[Hx_s,Hy_s,n_s] = wgmodes(wl_signal,guess,nmodes,dx,dy,epsxx_s,epsyy_s,epszz_s,boundary_s);
[Hz_s,Ex_s,Ey_s,Ez_s] = postprocess(wl_signal,n_s,Hx_s,Hy_s,dx,dy,epsxx_s,epsyy_s,epszz_s,boundary_s);
%% Calculate idler mode
wl_idler = wl_pump * wl_signal / (wl_signal - wl_pump);
[x_i,y_i,xc,yc,nx,ny,epsxx_i,epsyy_i,epszz_i] = meshfiorentino(dn,width,wl_idler,xmax,ymin,ymax,dx,dy);
guess = sqrt(max(max(epsyy_i)));
nmodes = 1;
boundary_i = '0000';
[Hx_i,Hy_i,n_i] = wgmodes(wl_idler,guess,nmodes,dx,dy,epsxx_i,epsyy_i,epszz_i,boundary_i);
[Hz_i,Ex_i,Ey_i,Ez_i] = postprocess(wl_idler,n_i,Hx_i,Hy_i,dx,dy,epsxx_i,epsyy_i,epszz_i,boundary_i);
%% Calculate pump mode
[x_p,y_p,xc,yc,nx,ny,epsxx_p,epsyy_p,epszz_p] = meshfiorentino(dn,width,wl_pump,xmax,ymin,ymax,dx,dy);
%guess = sqrt(max(max(epsxx))) - dn/4;
guess = 1.773159215920676;
nmodes = 1;
boundary_p = '0000';
[Hx_p,Hy_p,n_p] = wgmodes(wl_pump,guess,nmodes,dx,dy,epsxx_p,epsyy_p,epszz_p,boundary_p);
[Hz_p,Ex_p,Ey_p,Ez_p] = postprocess(wl_pump,n_p,Hx_p,Hy_p,dx,dy,epsxx_p,epsyy_p,epszz_p,boundary_p);

save(filename, ...
    'x_s', 'y_s', ...
    'Ex_s', 'Ey_s', 'Ez_s', ...
    'Hx_s', 'Hy_s', 'Hz_s', 'n_s', ...
    'epsxx_s', 'epsyy_s', 'epszz_s', ...
    'x_i', 'y_i', ...
    'Ex_i', 'Ey_i', 'Ez_i', ...
    'Hx_i', 'Hy_i', 'Hz_i', 'n_i', ...
    'epsxx_i', 'epsyy_i', 'epszz_i', ...
    'x_p', 'y_p', ...
    'Ex_p', 'Ey_p', 'Ez_p', ...
    'Hx_p', 'Hy_p', 'Hz_p', 'n_p', ...
    'epsxx_p', 'epsyy_p', 'epszz_p' ...
);

%% Create mesh
function [x,y,xc,yc,nx,ny,epsxx,epsyy,epszz] = meshfiorentino(dn,width,wl,xmax,ymin,ymax,dx,dy)
ax = [2 3 1];  % Crystal orientation
eps_bulk = zeros(3, 1);

for i=1:3; eps_bulk(i) = epsKTPfiorentino(wl, ax(i)); end
d = 8e-6;  % 1/e ion exchange depth
nx = round(xmax/dx) + 1;
ny = round((ymax-ymin)/dy) + 1;
x = (-xmax:dx:xmax)';
xc = x(1:end-1) + dx / 2;
y = (ymin:dy:ymax);
yc = y(1:end-1) + dy / 2;

eps = {ones(nx-1,ny-1), ones(nx-1,ny-1), ones(nx-1,ny-1)};

[xxc, yyc] = meshgrid(xc, yc);
idx_air = yyc>0;
idx_bulk = (~idx_air &  xxc>=width) | (~idx_air & xxc<=-width) ;

for i=1:3
    eps{i} = (sqrt(eps_bulk(i)) + dn*exp(yyc/d)').^2;
    eps{i}(idx_air') = 1;
    eps{i}(idx_bulk') = eps_bulk(i);
end

[epsxx, epsyy, epszz] = eps{:};
end

