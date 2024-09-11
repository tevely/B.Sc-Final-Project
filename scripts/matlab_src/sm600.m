% Refractive indices:
NA = 0.14;
ncl = 1.440;          % cladding index
nco = sqrt(ncl.^2 + NA.^2);          % core index
r = 2;           % core radius (um)

side = 20;         % space on side (um)

dx = 0.1;         % grid size (horizontal)
dy = 0.1;         % grid size (vertical)

lambda = 0.775;         % wavelength
nmodes = 1;         % number of modes to compute


%% Set up finite difference mesh:
[x,y,xc,yc,nx,ny,eps] = fiber([nco,ncl],[r],side,dx,dy);
imagesc(xc,yc,eps);
ax = gca();
ax.YDir = "normal";


%% Solve for mode (using transverse H modesolver)

% Boundary conditions for antisymmetric mode
boundary = '0A0A'; 
[Hx,Hy,neff] = wgmodes(lambda, nco, nmodes, dx, dy, eps, boundary);
fprintf(1,'neff (finite difference) = %8.6f\n',neff);
[Hz,Ex,Ey,Ez] = postprocess(lambda,neff,Hx,Hy,dx,dy,eps,boundary);
Sz = real(Ex.*conj(Hy(1:end-1,1:end-1))-Ey.*conj(Hx(1:end-1,1:end-1)));
imagemode(xc,yc,Ex);