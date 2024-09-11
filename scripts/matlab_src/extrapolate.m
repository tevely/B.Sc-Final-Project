function [xfull,yfull,varargout] = extrapolate(x,y,varargin)
if nargout ~= nargin-1
    error('Input and output arguments do not match')
end
nx = size(x,1);
ny = size(y,2);
if nargin == 5
    nmodes = size(varargin{1}, 3);
    Hx = varargin{1};
    Hy = varargin{2};
    boundary = varargin{3};
    xfull = [flip(-x(2:end)); x];
    yfull = [flip(-y(2:end)) y];
    varargout{1} = zeros([2*nx-1 2*ny-1 nmodes]);
    s1 = -1 + 2*(boundary(2)=='S');
    s2 = -1 + 2*(boundary(4)=='S');
    varargout{1}(1:nx,1:ny,:) = s1*s2*flip(flip(Hx,1),2);
    varargout{1}(1:nx,ny:end,:) = s1*flip(Hx,1);
    varargout{1}(nx:end,1:ny,:) = s2*flip(Hx,2);
    varargout{1}(nx:end,ny:end,:) = Hx;
    varargout{2} = zeros([2*nx-1 2*ny-1 nmodes]);
    varargout{2}(1:nx,1:ny,:) = s1*s2*flip(flip(Hy,1),2);
    varargout{2}(1:nx,ny:end,:) = -s1*flip(Hy,1);
    varargout{2}(nx:end,1:ny,:) = -s2*flip(Hy,2);
    varargout{2}(nx:end,ny:end,:) = Hy;
elseif nargin == 4 || nargin == 6 || nargin == 8
    boundary = varargin{nargin-2};
    xfull = [flip(-x); x];
    yfull = [flip(-y) y];
    for i=1:nargout-2
        varargout{i} = zeros([2*nx 2*ny]);
        varargout{i}(1:nx,1:ny) = flip(flip(varargin{i},1),2);
        varargout{i}(1:nx,ny+1:end) = flip(varargin{i},1);
        varargout{i}(nx+1:end,1:ny) = flip(varargin{i},2);
        varargout{i}(nx+1:end,ny+1:end) = varargin{i};
    end
else
    error('Incorrect number of input arguments.\n');
end
end