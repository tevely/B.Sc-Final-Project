function P = taper(params, varargin)
if nargin == 1
    do_run = false;
elseif nargin == 2
    do_run = varargin{1};
else
    error("Too many input arguments")
end
P = BPMmatlab.model;
P.doPlot = false;
if isfield(params, "doPlot")
    P.doPlot = params.doPlot;
end
updates = params.Nz;
if isfield(params, "updates")
    updates = params.updates;
end
dn_track = params.dn_track;
dn_halo = params.dn_halo;
track_w = [params.track_w_in, params.track_w_in, params.track_w_out, params.track_w_out];
track_h = [params.track_h_in, params.track_h_in, params.track_h_out, params.track_h_out];
gap = [params.gap_in, params.gap_in, params.gap_out, params.gap_out];

zi = [0, params.input_length, params.tp_length + params.input_length, params.total_length];
Nz = params.Nz;
wl = params.wl;
nParameters = {dn_track, dn_halo, track_w, track_h, zi, gap};
P.lambda = wl;
P.n_background = params.n_background;
P.n_0 = params.n_0;
P.Lz = zi(end);
P.taperScaling = 1;
P.twistRate = 0;
P.figTitle = 'Taper';
P.name = mfilename;
P.useAllCPUs = false;
P.useGPU = false;
P.updates = updates;
P.plotZoom = 1;
P.Lx_main = (max(gap / 2) + max(track_w / 2) + params.space_x);
P.Ly_main = (max(track_h / 2) + params.space_y);
P.Nx_main = ceil(P.Lx_main / params.dx);
P.Ny_main = ceil(P.Ly_main / params.dy);
P.padfactor = 1.5;
P.dz_target = params.dz;
P.alpha = 3e-4;
P = initializeRIfromFunction(P,@calcRI,nParameters,Nz);
P = initializeEfromFunction(P,@gaussBeam,{params});
P = findExpansionModes(P,params);
P.calcModeOverlaps = true;
if do_run
    P = FD_BPM(P);
end
end


%% USER DEFINED RI FUNCTIONS
function n = calcRI(X,Y,Z,n_background,nParameters)
dn_track = nParameters{1};
dn_halo = nParameters{2};
track_w_i = single(nParameters{3});
track_h_i = single(nParameters{4});
zi = single(nParameters{5});
gap_i = single(nParameters{6});
track_w = interp1(zi,track_w_i,Z);
track_h = interp1(zi,track_h_i,Z);
gap = interp1(zi,gap_i,Z);
eps = meshdoubletrack(X,Y,n_background,dn_track,dn_halo,track_w,track_h,gap);
n = sqrt(permute(eps, [2 1 3]));
end

%% USER DEFINED E-FIELD INITIALIZATION FUNCTION
function E = gaussBeam(X,Y,Eparameters) % Function to determine the initial E field. Eparameters is a cell array of additional parameters such as beam size
w_0 = Eparameters{1}.beam_radius;
E = exp(-(X.^2+Y.^2)/w_0^2);
end

function P = findExpansionModes(P, params)
[X, Y] = ndgrid(P.x, P.y);
eps = meshdoubletrack( ...
    X,Y, ...
    params.n_background, ...
    params.dn_track, ...
    params.dn_halo, ...
    params.track_w_out, ...
    params.track_h_out, ...
    params.gap_out ...
)';
x = X(:,1);
y = Y(1,:);
[x,y] = stretchmesh(x,y,[0,params.npml,0,params.npml],1+1i*2);
dx = diff(x);
dy = diff(y);
dx = [dx; dx(end)];
dy = [dy dy(end)];
[E,neff] = svmodes(params.wl,params.n_0,params.nmodes,dx,dy,eps,params.boundary,'scalar');
nmodes = size(E, 3);
for iMode=1:nmodes
    P.modes(iMode).Lx = P.Lx;
    P.modes(iMode).Ly = P.Ly;
    P.modes(iMode).xSymmetry = P.xSymmetry;
    P.modes(iMode).ySymmetry = P.ySymmetry;
    Emode = E(:,:,iMode);
    Emode = Emode.*exp(-1i*angle(max(Emode(:))));
    P.modes(iMode).field = Emode/sqrt(sum(abs(Emode(:)).^2));
    P.modes(iMode).neff = real(neff(iMode));
    P.modes(iMode).label = ['Mode ' num2str(iMode) P.modes(iMode).label];
end
end