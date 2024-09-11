clear all
pol_pump = 1;
params.input_length = 0.01;
params.tp_length = 500;
params.total_length = 1000;
params.space_x = 30;
params.space_y = params.space_x;
params.dx = 0.1;
params.dy = params.dx;
params.dz = 1;
params.Nz = 500;
params.pol = pol_pump;
params.nmodes = 10;
params.updates = 30;
params.doPlot = true;
%%
bests = jsondecode(fileread("../../data/doubletrack-best.json"));
params = initParams(params, bests.x0_775.x_0_004);
P = taper(params);
P = FD_BPM(P);

%% USER DEFINED E-FIELD INITIALIZATION FUNCTION
function E = calcInitialE(X,Y,Eparameters) % Function to determine the initial E field. Eparameters is a cell array of additional parameters such as beam size
params = Eparameters{1};
x = X(:,1);
y = Y(1,:);
eps = meshdoubletrack( ...
    X,Y, ...
    params.n_background, ...
    params.dn_track, ...
    params.dn_halo, ...
    params.track_w_in, ...
    params.track_h_in, ...
    params.gap_in ...
)';
[x,y] = stretchmesh(x,y,[0,params.npml,0,params.npml],1+1i*2);
dx = diff(x);
dy = diff(y);
dx = [dx; dx(end)];
dy = [dy dy(end)];
E = svmodes(params.wl,params.n_0,1,dx,dy,eps,params.boundary,'scalar');
end

function params = initParams(params, best)
params.boundary = '0000';
params.wl = best.eta_p.params.wl_pump;
if params.wl ~= 0.775 && params.wl ~= 0.405
    error("Have no beam radius defined for this wl pump")
end
if params.wl == 0.775
    params.beam_radius = 2.65;
else
    params.beam_radius = 1.2;
end
params.dn_track = best.eta_p.params.dn_track;
params.dn_halo = -params.dn_track / 4;
params.gap_in = best.eta_p.params.gap;
params.gap_out = best.A_I.params.gap;
params.track_w_in = best.eta_p.params.track_w;
params.track_w_out = best.A_I.params.track_w;
params.track_h_in = best.eta_p.params.track_h;
params.track_h_out = best.A_I.params.track_h;
params.npml = best.eta_p.params.npml;
crystal_axes = [2 3 1];
params.n_background = sqrt(epsKTPkato(params.wl, crystal_axes(params.pol)));
params.n_0 = params.n_background + params.dn_halo;
end