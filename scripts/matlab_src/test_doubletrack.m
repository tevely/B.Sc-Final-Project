dn_track = -0.002;
dn_halo = -dn_track ./ 4;
track_w = 3;
track_h = 20;
gap = 10;

space_x = 15;
space_y = space_x;
dx = 0.2;
dy = dx;
npml = 5;
wl_pump = 0.405;
wl_signal = wl_pump * 2;
wl_idler = wl_pump * wl_signal / (wl_signal - wl_pump);
crystal_axes = [2 3 1];

params.dn_track = dn_track;
params.dn_halo = dn_halo;
params.track_w = track_w;
params.track_h = track_h;
params.gap = gap;
params.space_x = space_x;
params.space_y = space_y;
params.dx = dx;
params.dy = dy;
params.npml = npml;
params.nmodes = 10;
%% Calculate modes
tic
signal = doubletrack(params, wl_signal, 1);
neff_s = signal.neff;
fprintf("Signal neff = %.5f+%.2gi\n", real(neff_s), imag(neff_s));

idler = doubletrack(params, wl_idler, 2);
neff_i = idler.neff;
fprintf("Idler neff = %.5f+%.2gi\n", real(neff_i), imag(neff_i));

pump = doubletrack(params, wl_pump, 1);
neff_p = pump.neff;
fprintf("Pump neff = %.5f+%.2gi\n", real(neff_p), imag(neff_p));
toc
%%
figure
tiledlayout(2,3)
nexttile
x = signal.x; y = signal.y;
imagesc(x,y,sqrt(signal.epsxx'));
title("signal refractive index")
nexttile
imagesc(x,y,sqrt(idler.epsyy'));
title("idler refractive index")
nexttile
imagesc(x,y,sqrt(pump.epsxx'));
title("pump refractive index")
nexttile
imagesc(x,y,real(signal.Hy)');
title("signal Hy")
nexttile
imagesc(x,y,real(idler.Hx)');
title("idler Hx")
nexttile
imagesc(x,y,real(pump.Hy)');
title("pump Hy")