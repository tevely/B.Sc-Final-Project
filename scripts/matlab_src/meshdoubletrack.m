function varargout = meshdoubletrack(X,Y,n_background,dn_track,dn_halo,track_w,track_h,gap)
varargout = cell(size(n_background));
n = cell(3,1);
nx = size(X,1);
ny = size(Y,2);
ones_ = ones(nx,ny);
x_r = gap / 2;
x_l = -x_r;
halo_h = track_h;
halo_w = halo_h;
halo_r = gaussian2d(X,Y,x_r,0,halo_w,halo_h);
halo_l = gaussian2d(X,Y,x_l,0,halo_w,halo_h);
halos = halo_r + halo_l;

idx_track_r = (2*(X-x_r)./track_w).^2+(2*Y./track_h).^2 <= 1;
idx_track_l = (2*(X-x_l)./track_w).^2+(2*Y./track_h).^2 <= 1;
idx_tracks = idx_track_r | idx_track_l;

for i=1:length(n_background)
    n{i} = n_background(i).*ones_ + dn_halo.*halos;
    n{i}(idx_tracks) = n_background(i) + dn_track;
    varargout{i} = permute(n{i}, [2 1 3]).^2;
end
end

function result = gaussian2d(x,y,xcen,ycen,sx,sy)
% 2D Gaussian with unit amplitude centered at 
result = exp(-(2*(x-xcen)./sx).^2-(2*(y-ycen)./sy).^2);
end

